# subset-b-006584 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/btf.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/btf.c

## Purpose
`btf.c` is libbpf's core implementation for BPF Type Format handling. It parses raw `.BTF`, ELF `.BTF`, `.BTF.ext`, and optional `.BTF.base` sections; owns the mutable in-memory BTF model; serializes BTF back into kernel or ELF-compatible byte streams; loads and fetches BTF through BPF syscalls; constructs BTF types programmatically; deduplicates types and strings; finds kernel and module BTF; creates distilled base BTFs for robust split-BTF relocation; and permutes type IDs while rewriting references.

This file is not Ceph-specific application logic. It is vendored libbpf infrastructure used by the Ceph client source tree wherever eBPF object loading, CO-RE relocation, or BTF inspection is needed.

## Important APIs, Types, and Functions
The central private type is `struct btf`. It tracks native-endian raw data, optional swapped-endian cached data, header metadata, type bytes, type ID offset index, base BTF relation, split-BTF start IDs and string offsets, string storage, ownership flags, modifiability, optional kind layout data, kernel FD, and target pointer size.

Creation and parsing APIs include `btf__new()`, `btf__new_split()`, `btf__new_empty()`, `btf__new_empty_split()`, `btf__new_empty_opts()`, `btf__parse()`, `btf__parse_split()`, `btf__parse_elf()`, `btf__parse_elf_split()`, `btf__parse_raw()`, and `btf__parse_raw_split()`. Internally, `btf_new()` validates headers, strings, optional layout, type records, and reference sanity before returning a usable object. `btf_parse_elf()` uses libelf to locate `.BTF`, `.BTF.ext`, and `.BTF.base`, and can relocate a split BTF against a supplied base.

Inspection APIs include `btf__type_cnt()`, `btf__base_btf()`, `btf__type_by_id()`, `btf__find_by_name()`, `btf__find_by_name_kind()`, `btf__pointer_size()`, `btf__set_pointer_size()`, `btf__endianness()`, `btf__set_endianness()`, `btf__resolve_size()`, `btf__resolve_type()`, `btf__align_of()`, `btf__fd()`, `btf__set_fd()`, `btf__raw_data()`, `btf__str_by_offset()`, and `btf__name_by_offset()`.

Kernel integration APIs include `btf__load_into_kernel()`, internal `btf_load_into_kernel()`, `btf__load_from_kernel_by_id()`, `btf__load_from_kernel_by_id_split()`, internal `btf_get_from_fd()`, `btf__load_vmlinux_btf()`, and `btf__load_module_btf()`.

Builder APIs append BTF types and type payloads: `btf__add_str()`, `btf__find_str()`, `btf__add_type()`, `btf__add_btf()`, `btf__add_int()`, `btf__add_float()`, `btf__add_ptr()`, `btf__add_array()`, `btf__add_struct()`, `btf__add_union()`, `btf__add_field()`, `btf__add_enum()`, `btf__add_enum_value()`, `btf__add_enum64()`, `btf__add_enum64_value()`, `btf__add_fwd()`, `btf__add_typedef()`, `btf__add_volatile()`, `btf__add_const()`, `btf__add_restrict()`, `btf__add_type_tag()`, `btf__add_type_attr()`, `btf__add_func()`, `btf__add_func_proto()`, `btf__add_func_param()`, `btf__add_var()`, `btf__add_datasec()`, `btf__add_datasec_var_info()`, `btf__add_decl_tag()`, and `btf__add_decl_attr()`.

`.BTF.ext` APIs are `btf_ext__new()`, `btf_ext__free()`, `btf_ext__raw_data()`, `btf_ext__endianness()`, `btf_ext__set_endianness()`, plus internal visitors `btf_ext_visit_type_ids()` and `btf_ext_visit_str_offs()`. The concrete `struct btf_ext` layout lives in `libbpf_internal.h`, while this file validates and byte-swaps func info, line info, and CO-RE relocation subsections.

Transform APIs include `btf__dedup()`, `btf__distill_base()`, `btf__relocate()`, and `btf__permute()`. They rely heavily on `btf_field_iter_init()` and `btf_field_iter_next()` from `btf_iter.c` to visit embedded type IDs and string offsets without hand-coding every kind in each pass.

## Control Flow
Raw parsing starts in `btf__new()` or `btf__new_split()`, which delegate to `btf_new()`. `btf_new()` allocates a `struct btf`, copies or adopts raw memory, initializes split offsets from the base BTF when present, parses the header with `btf_parse_hdr()`, assigns string and type section pointers, validates strings with `btf_parse_str_sec()`, attaches optional layout with `btf_parse_layout_sec()`, indexes every type with `btf_parse_type_sec()`, and performs libbpf-level sanity checks with `btf_sanity_check()`.

Header parsing accepts native or byte-swapped magic. If non-native BTF is detected, known header and type payload fields are swapped into native form for in-memory use. Unknown nonzero header extension bytes set `has_hdr_extra`, which blocks later mutation because the writer cannot preserve unknown semantics safely.

Type parsing is size-driven. `btf_type_size()` handles known BTF kinds. Unknown kinds can be parsed only if an optional kind-layout section supplies fixed `info_sz` and `elem_sz` for that kind. Each valid type contributes an offset to `type_offs`, allowing O(1) lookup by type ID while keeping type records variable-length.

ELF parsing tries `.BTF` and optional `.BTF.ext` sections through libelf. If `.BTF.base` is present, it is parsed as a distilled base. When the caller also supplies a real base BTF, the split BTF is relocated from the distilled base onto the real base with `btf__relocate()`. Pointer size is inferred from the ELF class.

`btf__parse()` first tries raw BTF by checking the BTF magic in the file. Only `-EPROTO`, meaning not raw BTF, falls through to ELF parsing. Raw kernel sysfs BTF can also be mmap-backed through `btf_parse_raw_mmap()`.

Serialization through `btf__raw_data()` delegates to `btf_get_raw_data()`. If a matching cached contiguous blob exists, it is returned. Otherwise the function creates a new contiguous layout from `hdr`, `types_data`, optional `layout`, and strings, byte-swapping into target endianness when requested.

Mutation begins with `btf_ensure_modifiable()`. It splits a contiguous parsed object into independently owned `types_data`, optional layout data, and a `strset`, then invalidates cached raw blobs. Builder functions append bytes to `types_data`, add/deduplicate strings through `strset`, update header lengths and offsets, and commit new type IDs through `btf_commit_type()`.

`btf__add_btf()` bulk-copies another BTF's local type section, rewrites referenced strings into the destination string section, remaps type IDs by the destination offset, and commits all changes only after successful rewriting. It has explicit rollback for string length on error and does not expose partially copied types before commit.

`.BTF.ext` parsing validates each subsection's alignment, record size, section header count, and record count. Non-native data is validated using swapped reads first, then the header and records are swapped to native order. Raw-data export can synthesize and cache a swapped copy.

Deduplication through `btf__dedup()` runs a fixed sequence: prepare split-base canonical state, deduplicate strings, deduplicate primitive types, deduplicate structs/unions/typedefs by graph equivalence, resolve unambiguous forward declarations, deduplicate reference types, compact canonical types, and remap all BTF and optional `.BTF.ext` type references. The graph-equivalence pass uses a hypothetical map to reason about cycles and forward declarations before committing canonical mappings.

Kernel loading calls `bpf_btf_load()`. If loading fails without logging, it retries with verifier logging enabled. For auto-managed logs, it doubles the log buffer on `ENOSPC` and prints the verifier log only for internally allocated buffers.

Distillation (`btf__distill_base()`) walks split-BTF references to old base types, creates a reduced base containing only names and sizing needed for later matching, moves detailed anonymous and reference types into a new split BTF, then rewrites IDs to account for the smaller base. Relocation (`btf__relocate()`) delegates to `btf_relocate()` in `btf_relocate.c`.

Permutation (`btf__permute()`) validates that the supplied ID map is a complete one-to-one order for base or split BTF, creates reordered type bytes, rewrites embedded type references and optional `.BTF.ext` type IDs, then swaps in the new type storage and recomputes type offsets.

## State and Persistence Behavior
`struct btf` has two major memory modes. Parsed BTF starts as a contiguous raw block where `types_data`, `layout`, and `strs_data` point inside `raw_data`. Once modified, `raw_data` is invalidated and the object owns separate allocations for types, layout, and strings. Later `btf__raw_data()` can regenerate a contiguous cached representation.

Split BTF state is encoded through `base_btf`, `start_id`, and `start_str_off`. Type IDs below `start_id` and string offsets below `start_str_off` are delegated to the base BTF. `owns_base` controls whether freeing the split BTF also frees its base, which matters when `.BTF.base` was embedded in an ELF.

The FD in `btf->fd` persists the kernel-loaded BTF handle and is closed by `btf__free()`. `btf__set_fd()` transfers a caller-provided FD into the object without duplication, so ownership expectations must be clear.

Endianness state is represented by `swapped_endian`. In-memory parsed fields are native-endian; raw export uses `raw_data` for native target data and `raw_data_swapped` for non-native target data. Changing endianness invalidates the swapped cache when the target becomes native.

Strings are either raw section bytes (`strs_data`) or a mutable `strset` (`strs_set`). `strs_deduped` lets dedup skip redundant string compaction after construction or previous dedup. Header `str_len`, `type_len`, `layout_off`, and `str_off` are maintained as persistent serialized metadata.

## Dependencies and Integration Points
The file depends on Linux UAPI BTF structures from `<linux/btf.h>`, BPF syscall wrappers from `bpf.h`, public libbpf APIs from `libbpf.h`, internal helpers from `libbpf_internal.h`, libelf/GELF for ELF parsing, `hashmap` for dedup state, and `strset` for mutable string storage.

Important internal integration points are `btf_field_iter_*()` for generic type/string reference traversal, `btf_relocate()` for distilled-base relocation, `bpf_btf_load()`, `bpf_btf_get_info_by_fd()`, and `bpf_btf_get_fd_by_id_opts()` for kernel BTF IO, plus `bpf_func_info_bswap()`, `bpf_line_info_bswap()`, and `bpf_core_relo_bswap()` for `.BTF.ext` byte swapping.

External filesystem integration includes `/sys/kernel/btf/vmlinux`, fallback vmlinux paths under `/boot`, `/lib/modules`, `/usr/lib/modules`, and `/usr/lib/debug`, and `/sys/kernel/btf/<module>` for module BTF. The code uses `uname()` to substitute the running kernel release into fallback paths.

## Risks and Edge Cases
Mutation is blocked when unknown nonzero header extension data is present. This protects unknown metadata but can surprise callers trying to edit newer-format BTF.

Non-native endianness support depends on known type layouts or a valid layout section. Unknown kinds without usable layout fail parsing or byte swapping.

Split BTF must have the correct base. Invalid `start_id` or `start_str_off` relationships can cause type and string references to resolve through the wrong base. `btf__add_btf()` rejects appending split BTF unless the source and destination share the same base pointer.

Several builder APIs allow forward references and validate only ID range, not existence. Final sanity depends on later validation or kernel verifier loading.

`btf__raw_data()` returns pointers owned by the BTF object and cached until the next mutation. Callers must not free or mutate them and must expect invalidation after builder, dedup, relocation, or permutation operations.

`btf__load_into_kernel()` returns `-EEXIST` for already-loaded objects. Retrying load after partial state changes requires a new object or explicit FD management.

`btf__permute()` mutates optional `.BTF.ext` references before final replacement of `types_data`. If an error occurs after `.BTF.ext` rewriting, the extension may already be changed even though the BTF type storage is not swapped in.

`btf_dedup_identical_types()` appears to initialize both array comparison pointers from `t1` in the array case (`a1 = btf_array(t1); a2 = btf_array(t1);`). If intentional this is non-obvious; if not, array identity fallback may compare the first type to itself instead of comparing against `t2`.

Deduplication is explicitly destructive on error: comments warn that type/string data might be garbled and should be discarded. Tests and callers should treat a failed `btf__dedup()` object as unusable.

Large inputs are bounded by `BTF_MAX_NR_TYPES`, `BTF_MAX_STR_OFFSET`, `UINT_MAX` section lengths, and overflow checks in allocation and size-resolution paths, but all parser changes should be tested with truncated, oversized, and cyclic type graphs.

## Test Signals
Parsing tests should cover native and swapped endian raw BTF, malformed headers, invalid magic, type/string section overlap, unaligned type and layout sections, missing string NUL terminator, split BTF with empty local strings, and unknown kinds with and without layout metadata.

ELF tests should cover `.BTF` only, `.BTF` plus `.BTF.ext`, embedded `.BTF.base`, relocation to a supplied base, missing `.BTF`, wrong section type, 32-bit versus 64-bit ELF class pointer size, and raw-to-ELF fallback behavior in `btf__parse()`.

Builder tests should verify every `btf__add_*()` API, immediate child-appender ordering constraints such as `btf__add_field()` after struct/union and `btf__add_func_param()` after func proto, forward references, string deduplication against base BTF, raw-data regeneration after mutation, and endianness switching.

Dedup tests should include duplicate primitives, enums and enum64 forward declarations, struct/union cycles, typedef chains, function prototypes, duplicate strings referenced only by `.BTF.ext`, split BTF with immutable base, forced hash collisions, ambiguous forward names, and dedup failure disposal.

Kernel integration tests need syscall-level coverage for load success, verifier-log retry, log-buffer `ENOSPC`, already-loaded object handling, `btf_get_from_fd()` buffer resizing, load-by-ID with and without token FD, vmlinux sysfs lookup, fallback vmlinux path lookup, and module split-BTF loading.

Transform tests should verify distilled-base creation for named composites, anonymous composites, arrays and modifiers, relocation against changed bases, `btf__permute()` validation of duplicate/missing IDs, reference rewrites in BTF and `.BTF.ext`, and failure behavior when maps are invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/btf.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/btf.h

## Purpose
`btf.h` is libbpf's public BTF interface. It declares opaque BTF and BTF.ext object types, section-name constants, creation/parsing/loading APIs, mutation APIs for constructing BTF records, transform APIs for deduplication, relocation and permutation, dump APIs, and inline helpers for interpreting `struct btf_type` payloads.

The header is designed for C and C++ consumers. It keeps the main object layouts opaque while exposing stable accessors and small inline helpers for BTF UAPI record payloads.

## Important APIs, Types, and Functions
Section constants are `BTF_ELF_SEC` for `.BTF`, `BTF_EXT_ELF_SEC` for `.BTF.ext`, `BTF_BASE_ELF_SEC` for `.BTF.base`, and `MAPS_ELF_SEC` for `.maps`.

Opaque declarations include `struct btf`, `struct btf_ext`, `struct btf_type`, and `struct bpf_object`. The public endianness enum is `enum btf_endianness` with little and big endian values.

Creation and parse APIs are `btf__new()`, `btf__new_split()`, `btf__new_empty()`, `btf__new_empty_split()`, `btf__new_empty_opts()`, `btf__parse()`, `btf__parse_split()`, `btf__parse_elf()`, `btf__parse_elf_split()`, `btf__parse_raw()`, and `btf__parse_raw_split()`. `struct btf_new_opts` provides optional base BTF and `add_layout` support.

Kernel and lookup APIs include `btf__load_vmlinux_btf()`, `btf__load_module_btf()`, `btf__load_from_kernel_by_id()`, `btf__load_from_kernel_by_id_split()`, `btf__load_into_kernel()`, `btf__find_by_name()`, `btf__find_by_name_kind()`, `btf__type_cnt()`, `btf__base_btf()`, `btf__type_by_id()`, `btf__fd()`, and `btf__set_fd()`.

Type and string inspection APIs include `btf__pointer_size()`, `btf__set_pointer_size()`, `btf__endianness()`, `btf__set_endianness()`, `btf__resolve_size()`, `btf__resolve_type()`, `btf__align_of()`, `btf__raw_data()`, `btf__name_by_offset()`, and `btf__str_by_offset()`.

`.BTF.ext` APIs include `btf_ext__new()`, `btf_ext__free()`, `btf_ext__raw_data()`, `btf_ext__endianness()`, and `btf_ext__set_endianness()`.

Builder APIs cover strings, type copying, complete BTF appending, primitive types, references, arrays, structs, unions, fields, enums, enum64, forward declarations, typedefs, CVR modifiers, type tags and attributes, functions, function prototypes, parameters, variables, data sections, data-section variable entries, declaration tags, and declaration attributes.

Transform option structs are `struct btf_dedup_opts` with optional `btf_ext` and `force_collisions`, and `struct btf_permute_opts` with optional `btf_ext`. Public transform APIs are `btf__dedup()`, `btf__relocate()`, `btf__permute()`, and `btf__distill_base()`.

Dump APIs declare `struct btf_dump`, `struct btf_dump_opts`, callback type `btf_dump_printf_fn_t`, `btf_dump__new()`, `btf_dump__free()`, `btf_dump__dump_type()`, `btf_dump__emit_type_decl()`, and `btf_dump__dump_type_data()` with their option structs.

Inline helper APIs include kind predicates such as `btf_is_int()`, `btf_is_struct()`, `btf_is_func_proto()`, `btf_is_decl_tag()`, and `btf_is_any_enum()`, compatibility helper `btf_kind_core_compat()`, integer metadata helpers `btf_int_encoding()`, `btf_int_offset()`, `btf_int_bits()`, payload accessors `btf_array()`, `btf_enum()`, `btf_enum64()`, `btf_members()`, `btf_params()`, `btf_var()`, `btf_var_secinfos()`, `btf_decl_tag()`, and member helpers `btf_member_bit_offset()` and `btf_member_bitfield_size()`.

## Control Flow and Usage Model
Consumers generally create or parse a BTF object, inspect or mutate it through the declared APIs, optionally deduplicate or relocate it, serialize it with `btf__raw_data()`, or load it into the kernel with `btf__load_into_kernel()`. Split-BTF callers pass a base object at creation or parse time, then type and string lookup APIs transparently resolve references through the base.

The builder API is order-sensitive for compound payloads. A caller starts a struct or union with `btf__add_struct()` or `btf__add_union()`, then immediately appends members with `btf__add_field()`. The same pattern applies to enums and enumerators, function prototypes and params, and data sections and variable info.

The header documents libbpf error conventions: most constructors return an error-code-encoded pointer unless strict clean pointers are enabled, while `btf__new_empty_opts()` documents NULL-on-error. Integer APIs return negative error codes and set `errno` through implementation helpers.

The inline helpers are thin views over Linux BTF UAPI memory layout. They assume the caller passes a valid `struct btf_type *` for the expected kind and perform pointer arithmetic to reach payload records immediately after the base type header.

## State and Persistence Behavior
Object lifetime is explicit. `btf__free()` releases a BTF object, and `btf_ext__free()` releases a BTF.ext object. Raw-data pointers returned by `btf__raw_data()` and `btf_ext__raw_data()` are object-owned snapshots and should be treated as invalid after object mutation or free.

`struct btf_new_opts`, `struct btf_dedup_opts`, `struct btf_permute_opts`, and dump option structs use `size_t sz` plus `*_last_field` macros for libbpf's forward/backward-compatible option validation pattern.

Base-BTF state is visible through `btf__base_btf()`, but ownership remains implementation-defined by the creation path. Callers that pass a base BTF must keep it alive as required by the implementation unless ownership is explicitly transferred by a parse path such as embedded `.BTF.base`.

## Dependencies and Integration Points
The header depends on `<linux/btf.h>` and `<linux/types.h>` for UAPI types and records, `<stdbool.h>` and `<stdarg.h>` for public signatures, and `libbpf_common.h` for `LIBBPF_API` and compatibility macros.

It is consumed by libbpf internals such as `btf.c`, BTF dumping code, BPF object loading code, linkers, and external applications that need BTF construction, inspection, CO-RE metadata, or kernel BTF loading.

The header compensates for older kernel headers by defining BTF kind constants that might not be present, including `BTF_KIND_FUNC`, `BTF_KIND_VAR`, `BTF_KIND_FLOAT`, `BTF_KIND_DECL_TAG`, `BTF_KIND_TYPE_TAG`, and `BTF_KIND_ENUM64`.

## Risks and Edge Cases
Inline payload accessors do not validate kind or bounds. Misusing `btf_members()` on a non-composite type, or reading enum64 payloads when the underlying data is too short, is caller error and can read invalid memory.

The `btf_enum64_value()` helper intentionally treats `struct btf_enum64` as a `__u32` array to support older system headers and C++ consumers. This is portable for the expected UAPI layout but depends on the BTF enum64 record staying three 32-bit words.

Several APIs accept type IDs that may reference future types. This is necessary for graph construction but means header-level type safety is weak until validation, dedup, serialization, or kernel loading.

The public API mixes pointer-returning constructors, integer-returning mutators, and object-owned raw pointers. Callers must consistently use `libbpf_get_error()` or check negative returns according to each function's contract.

Option-struct `sz` must be initialized correctly. Uninitialized option structs can be rejected by `OPTS_VALID()` in the implementation.

## Test Signals
Header/API tests should compile the header as C and C++, with both recent and older kernel headers, to verify fallback BTF kind definitions and the enum64 helper.

API contract tests should cover error-pointer constructors, clean-pointer strict mode, option struct sizing, base-BTF construction, split-BTF lookup, raw data ownership expectations, and all builder ordering constraints.

Inline helper tests should cover every BTF kind predicate, modifier grouping in `btf_is_mod()`, enum/enum64 compatibility through `btf_is_any_enum()` and `btf_kind_core_compat()`, bitfield offset and size decoding with and without `kflag`, and payload accessor correctness for arrays, members, params, variables, data sections, and declaration tags.

Integration tests should compile external-style users that include only `btf.h` plus standard dependencies and exercise parse, inspect, mutate, dedup, dump, and load declarations without relying on private `struct btf` or `struct btf_ext` layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/btf.h -->
