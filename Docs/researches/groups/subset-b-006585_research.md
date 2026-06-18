<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/btf_dump.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/btf_dump.c

## Purpose
`btf_dump.c` implements libbpf's BTF-to-C and BTF-typed-data formatter. It turns BTF type graphs into compilable C declarations and can also render raw memory according to a BTF type, with controls for compact output, indentation, field names, zero suppression, and string rendering.

## APIs, Types, and Functions
The public entry points are `btf_dump__new()`, `btf_dump__free()`, `btf_dump__dump_type()`, `btf_dump__emit_type_decl()`, and `btf_dump__dump_type_data()`. Persistent dump state lives in `struct btf_dump`, which owns the source `struct btf`, output callback, pointer size, per-type `btf_dump_type_aux_state`, cached unique names, topological `emit_queue`, declaration stack, duplicate-name hashmaps, and a temporary `struct btf_dump_data` during typed data dumping. Important helpers include `btf_dump_resize()`, `btf_dump_mark_referenced()`, `btf_dump_order_type()`, `btf_dump_emit_type()`, `btf_dump_emit_type_chain()`, `btf_dump_emit_struct_def()`, `btf_dump_emit_enum_def()`, `btf_dump_resolve_name()`, and the typed-data dispatch path through `btf_dump_dump_type_data()`.

## Control Flow, State, and Persistence
Construction validates options and callback, records pointer size from BTF or host default, allocates duplicate-name hashmaps, then sizes per-type state to the current BTF type count. Resizing also marks referenced types so anonymous top-level enums can be distinguished from inline anonymous enums. `btf_dump__dump_type()` clears the queue, performs a DFS-style topological sort using strong versus weak dependency rules, then emits queued definitions once each. Cycles through named pointer targets can be satisfied by forward declarations, while unsatisfiable embedded cycles return `-ELOOP`. Emission state tracks `NOT_EMITTED`, `EMITTING`, and `EMITTED` to avoid duplicate definitions and to decide when to emit struct/union/typedef forward declarations.

## Data Formatting Behavior
Declaration formatting walks BTF chains into a reusable declaration stack and emits valid C syntax for pointers, arrays, function prototypes, modifiers, type tags, typedefs, anonymous composites, enums, and forwards. Struct emission calculates explicit bit padding, detects packed layout, and preserves enum sizing attributes for 1-byte and selected 8-byte enums. Typed data dumping creates a stack-local `btf_dump_data`, checks overflow only for scalar/base access, optionally skips all-zero members, emits casts and member designators unless suppressed, and recursively handles ints, floats, pointers, arrays, strings, structs/unions, enums, vars, and datasecs. It copies unaligned integer/float/pointer data into aligned temporaries where needed and has explicit bitfield extraction for endian-specific bit layout.

## Dependencies and Integration
The file depends on libbpf's BTF accessors from `btf.h`, option validation and allocation helpers from `libbpf_internal.h`, public API definitions from `libbpf.h`, and the local `hashmap` implementation for duplicate name tracking. It is consumed by bpftool, skeleton/header generation, CO-RE diagnostics, and any libbpf caller that needs C declarations or printable typed values from BTF metadata.

## Risks and Test Signals
Risks include subtle C declaration precedence bugs for arrays of function pointers, incorrect forward declaration decisions for anonymous composite cycles, name-collision handling that changes emitted identifiers, host/target pointer-size and endian assumptions in data output, partial-data behavior that intentionally allows composite traversal while guarding scalar overflow, and packed/padding reconstruction that might not match compiler layout on unusual ABIs. Useful test signals are libbpf selftests for BTF dump headers, duplicate typedef/enum names, anonymous structs/unions/enums, enum64 and type tags, bitfields and packed structs, char-array string output, zero suppression, unaligned data buffers, and big-endian or swapped pointer-size scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/btf_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/btf_iter.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/btf_iter.c

## Purpose
`btf_iter.c` provides a small iterator over mutable fields embedded in raw BTF type records. It abstracts the per-kind layout differences so callers can visit either type-id references or string-offset references without open-coding offsets for every BTF kind.

## APIs, Types, and Functions
The exported functions are `btf_field_iter_init()` and `btf_field_iter_next()`. The iterator state is `struct btf_field_iter` from the shared BTF internals, with a `btf_field_desc` describing top-level offsets, optional per-member record size, per-member offsets, current member index, current offset index, and vlen. `BTF_FIELD_ITER_IDS` enumerates fields that contain BTF type IDs, while `BTF_FIELD_ITER_STRS` enumerates fields that contain string-table offsets.

## Control Flow, State, and Persistence
Initialization clears the iterator and then selects a descriptor based on requested field kind and `btf_kind(t)`. ID iteration covers `type` fields on modifiers, pointers, typedefs, funcs, vars, tags, array element and index types, composite member types, function return and parameter types, and datasec variable references. String iteration covers `name_off` on type records plus enum enumerators, enum64 enumerators, composite members, and function parameters. `btf_field_iter_next()` first returns top-level fields, then advances into fixed-size member records using `btf_vlen(t)` until exhausted, at which point it nulls the cursor.

## Dependencies and Integration
The file is dual-use for userspace libbpf and kernel code. Under `__KERNEL__` it includes Linux BPF/BTF headers and maps `btf_var_secinfos()` to the kernel helper; otherwise it uses `btf.h` and `libbpf_internal.h`. `btf_relocate.c` uses the iterator to rewrite split BTF type IDs and string offsets without duplicating BTF-kind layout knowledge.

## Risks and Test Signals
Risks are concentrated in descriptor correctness: a wrong offset silently rewrites the wrong word in a BTF record, and missing support for a new BTF kind can break relocation or validation with `-EINVAL`. Because the iterator returns mutable `__u32 *` pointers into caller-owned BTF memory, callers must only use it on writable records. Test signals include relocating BTF containing every supported kind, ID and string iteration count checks, datasec/func-proto/composite coverage, and build coverage for both userspace and `__KERNEL__` include paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/btf_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/btf_relocate.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/btf_relocate.c

## Purpose
`btf_relocate.c` relocates split BTF that was built against a distilled base BTF so it can instead reference a real base BTF. The output BTF keeps only split types, points at the supplied base BTF, and has its split type IDs and string offsets rewritten to the target base's numbering and string table.

## APIs, Types, and Functions
The public API is `btf_relocate(struct btf *btf, const struct btf *base_btf, __u32 **id_map)`. Internal state is carried by `struct btf_relocate`, which tracks the split BTF, real base BTF, distilled base BTF, counts for base/split/distilled types, string lengths, `id_map`, and `str_map`. Key helpers are `btf_relocate_validate_distilled_base()`, `btf_relocate_map_distilled_base()`, `btf_mark_embedded_composite_type_ids()`, `btf_relocate_rewrite_type_id()`, `btf_relocate_rewrite_strs()`, and the name/size search helpers built around `struct btf_name_info`.

## Control Flow, State, and Persistence
`btf_relocate()` rejects missing or identical base BTFs, allocates an ID map for all current types and a string map for the distilled base strings, validates that distilled base types are named int/float/enum/fwd/struct/union records, and pre-maps split IDs by adding the difference between real base and distilled base type counts. It then maps distilled base IDs to real base IDs by sorting distilled types by name and optional size, scanning real base types, handling kind compatibility, distinguishing FWD/struct/union forms, and enforcing size equality for embedded composites. After mapping, it rewrites all type-id fields in split records through `btf_field_iter`, rewrites string offsets either into the real base string table or shifted split string range, and finally calls `btf_set_base_btf()`.

## Dependencies and Integration
This file shares code between libbpf userspace and kernel builds through conditional macro aliases for BTF accessors, allocation, sorting, and bsearch support. It depends on `btf_iter.c` for generic ID/string field traversal and on BTF helpers for base-BTF access and header/string metadata. It integrates with split-BTF consumers that need a compact distilled base during build but a concrete runtime base for verifier or kernel use.

## Risks and Test Signals
Risks include ambiguous same-name/same-size base candidates, unmapped distilled base names, embedded struct/union size mismatches, off-by-one handling around BTF ID 0, and string remapping diagnostics that need correct old-offset reporting. Since the function mutates BTF in place and optionally transfers `id_map` ownership to the caller, failure-path cleanup and caller ownership are important. Test signals are relocation with duplicate-named base composites, embedded and pointer-only base composites, enum versus enum64 matching, module/kernel base swaps, unsupported distilled kinds, missing strings, and validation that all split record references point to valid post-relocation IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/btf_relocate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/elf.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/elf.c

## Purpose
`elf.c` centralizes libbpf ELF symbol lookup helpers used for uprobe attachment and symbol-pattern resolution. It opens ELF objects, walks symbol tables, handles GNU symbol version metadata, and converts symbol virtual addresses into file offsets expected by kernel uprobes.

## APIs, Types, and Functions
Public helpers include `elf_open()`, `elf_close()`, `elf_find_func_offset()`, `elf_find_func_offset_from_file()`, `elf_resolve_syms_offsets()`, and `elf_resolve_pattern_offsets()`. The main internal iterator is `struct elf_sym_iter`, which owns libelf data pointers for symbols, version symbols, version definitions, string table indexes, current symbol index, and target `STT_*` type. `struct elf_sym` carries the current name, `GElf_Sym`, containing section header, version index, and hidden-version flag.

## Control Flow, State, and Persistence
`elf_open()` initializes libelf, opens the file with `O_CLOEXEC`, and creates an mmap-backed ELF handle; `elf_close()` releases both. `elf_sym_iter_new()` finds a requested symbol section, binds its string table and data, and for dynamic symbols optionally attaches `SHT_GNU_versym` and `SHT_GNU_verdef` data. `elf_sym_iter_next()` filters by symbol type, resolves names and containing sections, and records GNU version state. Single function lookup parses optional `@` or `@@` library versions, searches dynamic then regular symbol tables, handles weak versus non-weak duplicates, and translates `st_value` to file offset via section address and section file offset.

## Dependencies and Integration
The file depends on libelf/GElf, `open/close`, libbpf logging/error helpers, `glob_match()`, and standard `qsort`/`bsearch`. It integrates with libbpf uprobe and USDT attachment paths that need symbol-to-offset resolution, as well as APIs that resolve a list of named symbols or a glob pattern against ELF function symbols.

## Risks and Test Signals
Risks include versioned symbol matching differences between `.dynsym` and `.symtab`, ambiguity when multiple non-weak symbols match different offsets, stripped/static binaries that expose only one symbol table, shared-library offset interpretation, and duplicate offsets from searching both dynamic and normal symbols. `elf_resolve_syms_offsets()` sorts only requested names and currently performs exact-name bsearch without version parsing, while pattern lookup stops after the first symbol table with matches to avoid duplicates. Test signals include uprobes on stripped binaries, shared libraries with `foo@@VER`, static binaries without dynsym, weak/non-weak duplicate symbols, glob pattern resolution, malformed ELF files, and zero-valued symbols that should be rejected for shared objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/elf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/features.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/features.c

## Purpose
`features.c` implements libbpf's runtime kernel feature detection cache. Each feature probe performs a small BPF syscall, BTF load, link creation, helper call, or verifier-log check to infer whether a kernel capability is available, optionally through a BPF token FD.

## APIs, Types, and Functions
The public functions are `probe_fd()` and `feat_supported()`. Most of the file is a table of `feature_probe_fn` callbacks in `feature_probes[__FEAT_CNT]`, keyed by `enum kern_feature_id`. Probes cover program names, global data, minimal BTF, BTF funcs/global funcs/datasecs/qmark datasecs/floats/decl tags/type tags/enum64/layout, mmapable arrays, expected attach type, `bpf_probe_read_kernel`, `BPF_PROG_BIND_MAP`, module BTF, perf links, BPF cookies, syscall wrappers, multi-uprobe links with PID-filter sanity checks, `__arg_ctx`, full-range LDIMM64 map-value offsets, and the x86 uprobe syscall.

## Control Flow, State, and Persistence
Each probe is intentionally small and closes any FD it opens through `probe_fd()` or explicit cleanup. `feat_supported()` uses a provided `struct kern_feature_cache` or a static global cache, checks `cache->res[feat_id]` with `READ_ONCE`, runs the probe only for `FEAT_UNKNOWN`, stores `FEAT_SUPPORTED` or `FEAT_MISSING` with `WRITE_ONCE`, and logs probe errors as missing features. Token-aware probes set `.token_fd` and `BPF_F_TOKEN_FD` on map/prog/BTF operations when the cache supplies a token.

## Dependencies and Integration
The file depends on low-level libbpf syscall wrappers from `bpf.h`, raw BTF load helpers, BPF instruction macros from Linux filter headers, feature IDs and cache definitions from `libbpf_internal.h`, and external probes such as `probe_memcg_account()` and `probe_kern_syscall_wrapper()`. Object loading, skeleton loading, CO-RE setup, attach selection, and compatibility fallbacks query this cache before using newer kernel features.

## Risks and Test Signals
Risks include probes that require privileges or token permissions and therefore can report missing despite kernel support, verifier-log string matching in `probe_ldimm64_full_range_off()`, architecture-specific syscall numbering for x86 uprobes, kernel behavior changes that alter expected errno values, and global cache reuse when different token FDs would produce different answers. Test signals are feature selftests across old and new kernels, unprivileged/tokenized loading, expected FD cleanup under failure, verifier-log variants for LDIMM64 behavior, multi-uprobe PID-filter detection, and cache behavior when probes return negative errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/features.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/gen_loader.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/gen_loader.c

## Purpose
`gen_loader.c` builds an embedded BPF loader program and data blob that can load another BPF object from inside the kernel context. It serializes BTF, maps, programs, map initialization, outer-map population, map freezing, extern/kfunc/CO-RE relocation handling, debug logging, cleanup, and optional data-blob signature checking into generated BPF instructions.

## APIs, Types, and Functions
Public builder functions include `bpf_gen__init()`, `bpf_gen__finish()`, `bpf_gen__free()`, `bpf_gen__load_btf()`, `bpf_gen__map_create()`, `bpf_gen__record_attach_target()`, `bpf_gen__record_extern()`, `bpf_gen__record_relo_core()`, `bpf_gen__prog_load()`, `bpf_gen__map_update_elem()`, `bpf_gen__populate_outer_map()`, and `bpf_gen__map_freeze()`. The generated loader stack is described by `struct loader_stack`, while mutable build state is in `struct bpf_gen` from `bpf_gen_internal.h`: instruction/data cursors, fd-array location, map/prog counts, relocation arrays, ksym descriptors, attach target, hash offsets, endianness flag, log level, and sticky error.

## Control Flow, State, and Persistence
Initialization reserves a blob fd-array, saves loader context in `R6`, clears the generated stack, emits a jump over cleanup code, then emits a shared cleanup path that closes stack and blob FDs and exits with `R7`. Builders append bytes to `data_start` and BPF instructions to `insn_start`, using `emit_sys_bpf()` for BPF syscalls and `emit_check_err()` to branch to cleanup on negative `R7`. `bpf_gen__finish()` closes temporary BTF FDs, copies generated map/prog FDs back into the caller-visible loader context, optionally patches SHA256 immediates, byte-swaps instructions for target endianness, and transfers final buffers through `gen_loader_opts`.

## Loader Operations
`bpf_gen__load_btf()` embeds raw BTF and emits `BPF_BTF_LOAD`. `bpf_gen__map_create()` prepares `BPF_MAP_CREATE`, fills BTF and inner-map FDs when needed, allows context override of `max_entries`, records map FDs in the blob fd-array, and closes temporary inner-map FDs. Program loading embeds license, instructions, func/line info, and CO-RE relo records, applies target-endian conversion, wires log buffers and fd arrays, resolves attach BTF IDs when an attach target was recorded, emits extern relocations, performs `BPF_PROG_LOAD`, and then closes temporary module BTF/attach FDs. Map update/populate/freeze emit the corresponding syscalls, including runtime copy from user or kernel-provided initial value for map initialization.

## Relocation and Endianness Behavior
Extern relocation paths support kfunc calls, typed ksyms through BTF ID lookup, and typeless ksyms through `kallsyms_lookup_name`. Duplicate symbols share cached `ksym_desc` state so repeated relocations copy previously resolved immediates and avoid exhausting kernel kfunc BTF FD limits. Weak relocations zero instruction fields on lookup failure, while strong relocations branch to cleanup. The file uses `tgt_endian()` and explicit byte-swap helpers for attrs, BPF instructions, func info, line info, and CO-RE relocation records when generating for an opposite-endian target.

## Dependencies and Integration
This file depends on BPF instruction macros, libbpf syscall attribute layouts, `bpf_gen_internal.h`, `skel_internal.h`, BTF helper naming, SHA256 helpers, and map/program descriptors shared with generated skeletons. It is tightly integrated with libbpf's object-loading pipeline: normal userspace loading records enough metadata for this generator to produce equivalent in-kernel loading instructions.

## Risks and Test Signals
Risks include fixed limits (`MAX_USED_MAPS`, `MAX_USED_PROGS`, `MAX_KFUNC_DESCS`), relative branch offsets exceeding signed 16-bit immediate range, stale sticky `gen->error` after allocation failures, offset mismatches in generated `union bpf_attr` blobs, endian conversion gaps, cleanup paths leaking module BTF or map FDs, weak relocation semantics producing zeroed instructions that must remain verifier-safe, and mismatch between recorded map/prog counts and final `bpf_gen__finish()` arguments. Test signals include skeleton gen-loader selftests, generated-loader load failures with cleanup verification, many maps/programs/kfuncs near limits, big-endian target generation, extern strong/weak ksym and kfunc resolution, attach-target BTF lookup, map-in-map creation, initial-value copying from user and kernel contexts, and optional loader data hash validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/gen_loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/hashmap.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/hashmap.c

## Purpose
`hashmap.c` implements libbpf's generic, non-thread-safe chained hashmap. It stores long-sized integer or pointer keys and values through the public macro layer in `hashmap.h`, grows buckets on demand, supports several insert semantics, and provides basic find/delete/clear/free operations.

## APIs, Types, and Functions
Implemented public functions are `hashmap__init()`, `hashmap__new()`, `hashmap__clear()`, `hashmap__free()`, `hashmap__size()`, `hashmap__capacity()`, `hashmap_insert()`, `hashmap_find()`, and `hashmap_delete()`. Internal helpers are `hashmap_add_entry()`, `hashmap_del_entry()`, `hashmap_needs_to_grow()`, `hashmap_grow()`, and `hashmap_find_entry()`. `HASHMAP_MIN_CAP_BITS` starts maps at four buckets.

## Control Flow, State, and Persistence
Initialization only stores caller-provided hash/equality callbacks and context, leaving buckets unallocated. Insert hashes the key using current capacity bits, optionally finds an existing entry for ADD/SET/UPDATE behavior, updates in place for SET/UPDATE, returns `-EEXIST` or `-ENOENT` for disallowed operations, grows the bucket table when empty or above roughly 75 percent load, allocates a new entry, and pushes it at the bucket head. Growth allocates a doubled power-of-two bucket array and rethreads existing entries using the new bit count. Clear frees entries and buckets but leaves callback configuration intact; free additionally frees the map object.

## Dependencies and Integration
The implementation depends on `hashmap.h` iteration macros, libc allocation, errno values, and `linux/err.h` for `ERR_PTR`/`IS_ERR_OR_NULL` conventions. It is used by libbpf internals such as BTF dump duplicate-name tracking and other key/value caches that need a tiny local map without pulling in a larger container library.

## Risks and Test Signals
Risks include no internal locking, caller ownership of pointed-to keys/values, append-mode duplicate keys returning the most recently inserted bucket-head entry for `hashmap_find()`, hash/equality callbacks needing to tolerate long-cast pointer keys, and iteration macros assuming bucket storage remains stable unless the safe form is used. Test signals are insert strategy coverage, growth and rehash correctness, duplicate-key append iteration, deletion from head/middle/tail chains, clear/free on empty and error-pointer maps, and pointer key/value round trips through the macro API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/hashmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/hashmap.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/hashmap.h

## Purpose
`hashmap.h` declares the generic libbpf hashmap API and provides inline hashing utilities plus macro wrappers that make the long-sized storage model usable with typed integer and pointer keys/values.

## APIs, Types, and Functions
Inline helpers are `hash_bits()` for multiplicative bucket-bit extraction and `str_hash()` for simple C-string hashing. Public types include `hashmap_hash_fn`, `hashmap_equal_fn`, `struct hashmap_entry`, `struct hashmap`, and `enum hashmap_insert_strategy`. The header declares lifecycle, query, insert, find, and delete functions, then exposes typed macros `hashmap__insert()`, `hashmap__add()`, `hashmap__set()`, `hashmap__update()`, `hashmap__append()`, `hashmap__delete()`, and `hashmap__find()`.

## Control Flow, State, and Persistence
`struct hashmap_entry` stores key and value as unions of `long` and pointer views, plus a singly linked `next` pointer. `struct hashmap` stores callback functions, callback context, bucket array, capacity, capacity bit count, and size. `hashmap_cast_ptr()` uses `_Static_assert` to verify that optional old-key/old-value output pointers point to long-sized objects or pointers. Iteration macros traverse all buckets, all buckets safely while caching `next`, all entries for one key, or one key safely.

## Dependencies and Integration
The header only requires standard boolean, size, and limit definitions. It is paired with `hashmap.c` and used by libbpf code that needs compact maps with custom hash/equality behavior. The API intentionally hides raw `long` casts behind macros for most callers while still permitting integer-key users to read `entry->key` and pointer-key users to read `entry->pkey`.

## Risks and Test Signals
Risks include ABI assumptions that pointers and chosen integer keys fit in `long`, non-thread-safe iteration and mutation, macro side effects if callers pass expressions with unexpected evaluation needs, and direct iteration over `map->buckets` requiring initialized or non-null bucket arrays. Test signals are compile-time failures for wrong output pointer sizes, LP64 and ILP32 builds, string-hash users, all iteration macro variants, append-mode multimap scans, and callers that mix integer and pointer views consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/hashmap.h -->
