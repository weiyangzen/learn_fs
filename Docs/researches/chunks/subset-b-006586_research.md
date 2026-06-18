# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf.c lines 1-9443

## Scope

This chunk covers the first 9,443 lines of Ceph's vendored `tools/lib/bpf/libbpf.c`. It is the core libbpf object-loader implementation up through the start of `bpf_object__unpin()`. The range includes object allocation/opening, ELF collection, BTF and BTF.ext parsing/sanitization, map definition and creation, extern/kconfig/ksym resolution, CO-RE relocation, subprogram relocation, program load preparation, verifier-log fixups, object prepare/load orchestration, and the beginning of public pin/unpin APIs.

This is not Ceph-specific filesystem client logic. It is an in-tree copy of Linux tools/lib/bpf loader code used to build or run eBPF programs from ELF objects. The later part of the same file continues API coverage for unpinning, attachment, ring/perf buffers, introspection, and cleanup; merge/reconciliation should combine this chunk with the following chunks before producing a per-file report.

## Purpose

The code turns a BPF ELF object into kernel BPF objects. It discovers executable sections and maps, interprets BTF metadata, resolves relocations and externs, creates maps, loads BTF, loads programs, and pins or reuses objects through bpffs. It also provides compatibility shims for older kernels by probing features, sanitizing unsupported BTF kinds, rewriting helper calls, and producing clearer verifier logs when intentional "poisoned" instructions fail verification.

The loader maintains a high-level `struct bpf_object` state machine: open and parse the object, prepare all kernel-facing state, create maps and load programs, and then expose FDs or pin paths to callers. It must bridge several contracts at once: ELF/libelf layout, Clang/BTF output conventions, Linux BPF syscall UAPI, kernel feature availability, bpffs pinning, `/proc` kernel metadata, and libbpf's public API expectations.

## Important APIs, Types, and Data

The first section defines string tables for BPF attach, link, map, and program type names, plus printing APIs. `libbpf_set_print()` swaps the global print callback atomically, while `libbpf_print()` preserves `errno` around logging. `__base_pr()` honors `LIBBPF_LOG_LEVEL`, and `pr_perm_msg()` emits a root/memlock hint for `-EPERM`.

Core object model types are declared early:

- `struct bpf_object` owns the parsed object name/path, state, programs, maps, externs, ELF state, BTF/BTF.ext handles, vmlinux/module BTFs, gen-loader state, feature cache, BPF token FD, arena/jumptable state, and log settings.
- `struct bpf_program` stores section identity, instruction buffers, relocation descriptors, verifier log settings, FD, autoload/autoattach flags, program/attach types, BTF func/line info, program hash, subprogram offsets, and exception callback state.
- `struct bpf_map` stores definition fields, FD placeholders, BTF type IDs, pin state, mmap/init buffers, struct_ops metadata, inner-map/init-slot data, map-extra, and auto-create/attach settings.
- `struct extern_desc` models `__kconfig` and `__ksym` externs, including BTF IDs, weak/strong status, kconfig layout offsets, typed ksym target IDs, module BTF FD indexes, and resolved addresses.
- `struct elf_state` tracks libelf handles, symbol/string sections, per-section descriptors, `.maps` and `.text` indices, arena and jumptable sections, and section classifications.
- `struct reloc_desc` normalizes ELF/BTF relocations into loader actions such as map loads, data map values, extern loads/calls, subprogram calls/addresses, CO-RE records, and instruction-array jump tables.

The open APIs in this range are `bpf_object__open_file()`, legacy `bpf_object__open()`, and `bpf_object__open_mem()`. The load APIs are `bpf_object__prepare()` and `bpf_object__load()`. Map APIs include auto-create/auto-attach accessors, `bpf_map__reuse_fd()`, `bpf_map__inner_map()`, `bpf_map__set_max_entries()`, map pin/unpin/path accessors, and object-level map pin/unpin helpers. Program pin/unpin and object pin are also covered; `bpf_object__unpin()` begins at the last line of this chunk but its body is outside the range.

## ELF, BTF, and Map Parsing

`bpf_object__elf_init()` validates that the input is a 64-bit relocatable BPF ELF object, records byte order, and opens from either memory or file. `bpf_object__elf_collect()` performs the main scan. It first finds the symbol table, then classifies sections: license, kernel version, BTF, BTF.ext, BTF-defined `.maps`, executable program sections, global data sections (`.data*`, `.rodata*`, `.bss*`), struct_ops sections, arena data, jumptables, and relocation sections. Unsupported legacy `maps` sections are rejected.

Program discovery uses `bpf_object__add_programs()` and `bpf_object__init_prog()`. Each `STT_FUNC` symbol in an executable section becomes a `struct bpf_program`; static entry programs outside `.text` are rejected, `SEC("?name")` starts with `autoload=false`, hidden/internal global functions are marked for later BTF-static fixup, and non-native byte order instructions are byte-swapped for introspection.

BTF initialization is split across `bpf_object__init_btf()`, `bpf_object_fixup_btf()`, and `bpf_object__sanitize_btf()`. BTF.ext sections are mapped back to ELF section indices for func info, line info, and CO-RE records. DATASEC fixup fills missing sizes and variable offsets from ELF symbols, sorts variables by offset, and converts hidden/internal variables to static linkage. Sanitization rewrites unsupported BTF features for older kernels, including DATASEC/VAR, FUNC/FUNC_PROTO, FLOAT, DECL_TAG, TYPE_TAG, ENUM64, qmark DATASEC names, and newer BTF layout header data.

Map parsing supports both internal maps and BTF-defined maps. Internal maps are synthesized for global data and kconfig sections through `bpf_object__init_internal_map()`, with stable but truncated/sanitized names from `internal_map_name()`, initial anonymous mmap buffers, optional `BPF_F_MMAPABLE`, and read-only program flags for `.rodata`/`.kconfig`. BTF-defined maps are parsed from `.maps` DATASEC variables by `parse_btf_map_def()` and `bpf_object__init_user_btf_map()`, including `type`, key/value type or size, `max_entries`, flags, `numa_node`, `pinning`, `map_extra`, map-in-map inner definitions, and prog-array/map-in-map `values` initializers. Ring buffer sizes are rounded to a page-size power-of-two multiple.

`bpf_object__init_maps()` sequences BTF map parsing, global data maps, kconfig map creation, and struct_ops map initialization. ARENA maps are limited to one map and must be declared explicitly if `.addr_space.1` global data exists.

## Struct Ops Handling

Struct_ops support is present throughout this chunk. `init_struct_ops_maps()` converts `.struct_ops`, `.struct_ops.link`, and optional `?` variants into `BPF_MAP_TYPE_STRUCT_OPS` maps backed by local BTF struct data. `bpf_map__init_kern_struct_ops()` finds the kernel-side struct and `bpf_struct_ops_*` value type in vmlinux or module BTF, copies compatible scalar data, validates function pointer fields, records `attach_btf_id` and expected member index on callback programs, handles missing all-zero members by skipping them, and disables autoload for callbacks that cannot be used.

`bpf_object_adjust_struct_ops_autoload()` reconciles program autoload with struct_ops map autocreate state so referenced callbacks load only when at least one autocreated struct_ops map uses them. After program load, `bpf_map_prepare_vdata()` writes loaded program FDs into kernel-value data, and `bpf_object_prepare_struct_ops()` prepares every autocreated struct_ops map.

## Externs, Kconfig, Ksyms, and Kernel BTF

`bpf_object__collect_externs()` discovers undefined global/weak symbols, finds matching BTF VAR/FUNC records, determines whether they belong to `.kconfig` or `.ksyms`, sorts extern descriptors, and mutates extern DATASECs so kernel BTF validation sees allocated variables. Kconfig externs get packed offsets according to alignment and size. Ksym externs may be typeless addresses or typed BTF references; extern function records get a dummy var workaround where needed.

Kconfig resolution parses either an in-memory open option or `/boot/config-$(uname -r)` / `/proc/config.gz`. It supports boolean, tristate, char, char array, integer, and a small set of virtual `LINUX_*` externs such as kernel version, BPF cookie support, and syscall-wrapper support. Strong unresolved externs fail object preparation; weak unresolved externs default to zero.

Ksym resolution uses two paths. Typeless variable ksyms are resolved from `/proc/kallsyms`, including an `.llvm.` suffix workaround for data symbols. Typed ksyms and kfuncs require vmlinux or module BTF. `find_ksym_btf_id()`, `bpf_object__resolve_ksym_var_btf_id()`, and `bpf_object__resolve_ksym_func_btf_id()` find target BTF IDs, check local/target compatibility with CO-RE type rules, populate module BTF fd-array indexes for kfunc calls, and tolerate weak missing/incompatible entries where allowed.

`bpf_object__load_vmlinux_btf()` lazily loads vmlinux BTF only when needed by CO-RE relocations, typed ksyms, tracing/LSM/struct_ops programs, or struct_ops maps. `load_module_btfs()` enumerates kernel BTF objects, skips vmlinux, loads module BTFs, and records their FDs and names for CO-RE and ksym lookup.

## Relocation and Load Control Flow

The open flow is:

1. `bpf_object_open()` validates options, captures log/token/custom-BTF/kconfig options, allocates `struct bpf_object`, initializes ELF, collects sections, collects externs, fixes BTF, initializes maps and programs, collects relocations, then releases libelf state.
2. `bpf_object__collect_relos()` dispatches relocation sections to program, map-in-map/prog-array, or struct_ops relocation collectors.
3. `bpf_program__record_reloc()` normalizes executable-section relocations into map references, data references, arena references, jumptable instruction arrays, extern loads/calls, subprogram calls, and subprogram-address loads.

The prepare/load flow is:

1. `bpf_object_prepare()` creates an optional BPF token, probes basic BPF load support, loads vmlinux BTF if needed, resolves externs, sanitizes map flags, initializes kernel struct_ops data, adjusts struct_ops autoload, applies CO-RE/code/data relocation, loads BTF, creates maps, and sanitizes helper calls.
2. `bpf_object_load()` runs prepare if needed, loads each autoloaded non-subprogram, initializes prog-array slots, writes struct_ops program FDs into value data, finalizes gen-loader output if used, frees temporary BTF/fd-array state, and marks the object loaded even on failure.

CO-RE relocation is handled by `bpf_object__relocate_core()`. It optionally parses a custom target BTF, records each CO-RE record in the owning program for later gen-loader or log fixup use, finds target candidates from vmlinux first and module BTFs only if needed, caches candidate lists by local type ID, computes relocation results, and patches instructions unless generating a loader program.

Subprogram relocation uses a per-main-program recursive append algorithm. `bpf_object__relocate_calls()` resets all `.text` subprogram offsets for one main program, then `bpf_object__reloc_code()` walks calls and pseudo-function loads. Called subprograms are appended to the main program's instruction array exactly when first needed for that main, their relocations and BTF func/line info are offset-adjusted into the main image, and call immediates are rewritten to the final relative offsets. Exception callbacks named by `exception_callback:<name>` declaration tags are validated and appended as needed.

Data relocation in `bpf_object__relocate_data()` rewrites ldimm64 instructions to map FDs or gen-loader map indexes, map-value addresses, kconfig map offsets, typed BTF IDs, ksym addresses, kfunc call IDs, and instruction-array jump table maps. If a referenced internal map was intentionally not created on an older kernel, or if a weak kfunc remains unresolved, the code poisons the instruction with identifiable invalid helper-call constants so verifier output can later be replaced with a targeted error.

Program loading uses `bpf_object_load_prog()`. It validates program type and struct_ops attach state, fills `bpf_prog_load_opts`, adds BTF func/line info if supported, applies section-specific load preparation, handles BPF token flags, loads through gen-loader or `bpf_prog_load()`, retries with verifier logging when needed, grows auto log buffers on `ENOSPC`, binds `.rodata` maps to programs when supported, and calls verifier-log fixups on failure.

## State and Persistence Behavior

Object state is explicit: `OBJ_OPEN`, `OBJ_PREPARED`, and `OBJ_LOADED`. Prepare and load are one-shot; attempts to repeat either path fail. On prepare or load failure, maps/programs are unloaded, auto-pinned maps that were not reused are unpinned, and the object is marked loaded to avoid inconsistent reuse.

Map FDs start as memfd placeholders created by `create_placeholder_fd()`. This preserves FD numbers while relocations are applied before real kernel maps exist. When a real map is created or reused, `reuse_fd()` makes the placeholder FD refer to the kernel map, so already-relocated instructions remain valid. In gen-loader mode, placeholders remain logical and are later reset.

Internal global-data maps keep initialization content in anonymous mmap buffers until map creation. After creation, content is uploaded; `.rodata` and `.kconfig` maps are frozen, mmapable maps are remapped at the same virtual address to the kernel map, and non-mmapable init buffers are unmapped. ARENA maps mmap their kernel memory and copy saved arena global data at `arena_data_off`.

Pinned map state persists in bpffs. `bpf_object__reuse_map()` reuses an existing pinned map only if type, key/value size, max entries, flags, and map extra match. Auto-pinning retries if creation raced with an existing pin. `map->pinned`, `map->reused`, and `map->pin_path` track whether cleanup should unlink the bpffs path.

Temporary state includes libelf handles, vmlinux/module BTFs, fd arrays for module BTF kfunc calls, relocation descriptors, BTF candidate caches, verifier log buffers, and jumptable maps. `bpf_object_post_load_cleanup()` releases module/vmlinux BTF and fd-array state after load; `bpf_object__free_relocs()` drops relocation descriptors after successful program load.

## Dependencies and Integration Points

This code depends on libc, libelf/GElf, zlib, Linux UAPI headers, BPF syscalls wrapped by `bpf.h`, libbpf's BTF implementation, CO-RE relocation helpers, libbpf internal utilities, hashmap support, SHA-256 hashing, generated-loader support, and bpffs. Kernel integration points include `BPF_BTF_LOAD`, `BPF_MAP_CREATE`, `BPF_PROG_LOAD`, `BPF_OBJ_GET/PIN`, `BPF_TOKEN_CREATE`, map freezing, program-map binding, BTF object enumeration, `/proc/kallsyms`, `/proc/*/fdinfo`, `/proc/config.gz`, and `/boot/config-*`.

The code also depends on compiler and linker conventions: Clang BPF instruction layout, ELF `SHT_REL` records, BTF `.maps` definitions, BTF DATASEC records, `.BTF.ext` func/line/core sections, `SEC("?name")` optional-load convention, hidden/internal visibility for static verifier treatment, `.jumptables` generated for switch lowering, and declaration tags such as `arg:ctx` and `exception_callback:*`.

Public integration surfaces in this range are object open/load/prepare APIs, program/map pinning APIs, map auto-create/auto-attach/reuse/max-entries APIs, BTF utility APIs (`btf_kind_str()`, `skip_mods_and_typedefs()`), CO-RE candidate/type compatibility APIs, and logging hooks.

## Risks and Edge Cases

The loader is sensitive to malformed ELF/BTF data. It validates section sizes, relocation offsets, symbol section indices, instruction alignment, BTF variable linkage, map definition shapes, zero-sized array `values` members, map-in-map nesting, and program-array references. Missing or invalid symbols can either fail open or be skipped only for known weak-linker cases.

Kernel feature probing drives many compatibility branches. Incorrect feature detection can cause invalid BTF uploads, wrong helper rewrites, unsupported mmap flags, missing expected attach types, bad kfunc/module BTF load options, or skipped global data maps that later produce verifier failures.

Relocation order matters. CO-RE must run before subprogram appending and data relocation; subprogram relocation must append per-main code before map/data/kfunc relocations; func/line info must be offset-adjusted after code layout changes; and BTF func-info fixups must happen before program load. Sorting relocation descriptors is required for binary searches by instruction index.

FD placeholder semantics are subtle. Closing or replacing placeholders incorrectly would invalidate already-relocated instructions. Reused pinned maps must be compatibility-checked, and map-in-map/prog-array init slots must use loaded target FDs at the correct phase.

Extern resolution has several failure modes: absent kernel config files, unavailable `/proc/kallsyms`, ambiguous kallsyms names, missing BTF permissions, module BTF races, weak versus strong extern behavior, incompatible typed ksym/kfunc prototypes, and fd-array index overflow for module kfunc BTF FDs.

BTF sanitization can preserve loadability but loses semantic detail. Rewriting DATASEC, FUNC, FLOAT, TYPE_TAG, DECL_TAG, or ENUM64 for older kernels must keep type sizes and offsets acceptable to kernel validation. BTF pointer invalidation during mutation is a repeated risk; helper comments note that type/string pointers must be refetched after `btf__add_*()` calls.

Pinning APIs require bpffs-backed paths. `check_path()` rejects non-bpffs parent directories, `make_parent_dir()` only creates one parent directory level, and object-level pin helpers may partially pin then unwind on error. Map object pin paths also sanitize dots when deriving object-level paths, but direct map pin paths are used as provided.

The chunk boundary is important: line 9443 is only the function signature for `bpf_object__unpin()`. Its body and any related error unwinding are outside this chunk.

## Test Signals

Useful validation for this range includes:

- ELF open tests for file and memory objects, invalid ELF class/type/machine/endianness, missing symbol tables, malformed section names, stripped objects, and non-native-endian introspection versus load rejection.
- Program discovery tests for multiple executable sections, `.text` subprograms, weak/hidden/global symbols, optional `SEC("?")` autoload, and static entry-program rejection outside `.text`.
- BTF tests for missing required BTF, BTF.ext section-index mapping, DATASEC size/offset fixup, hidden variable/function linkage changes, qmark DATASEC sanitization, unsupported BTF kind sanitization, and optional versus mandatory BTF load failures.
- BTF map definition tests for all supported fields, strict unknown-field rejection, conflicting key/value sizes, map-in-map inner definitions, prog-array `values`, pinning by name, ringbuf size adjustment, ARENA single-map enforcement, and malformed `.maps` relocations.
- Global data map tests for `.data`, `.rodata`, `.bss`, custom `.rodata.*`/`.data.*`, mmapable versus non-mmapable skeleton exposure, freezing `.rodata`/`.kconfig`, old kernels without global data support, and verifier-log fixup for uncreated map references.
- Struct_ops tests for `.struct_ops` and `.struct_ops.link`, optional struct_ops maps, kernel/member BTF matching, missing all-zero fields, incompatible member kinds/sizes, callback attach IDs, module struct_ops BTF, autoload adjustment, and FD insertion into kernel value data.
- Extern tests for kconfig bool/tristate/int/char/string parsing, extra in-memory kconfig, missing system config, virtual `LINUX_*` externs, weak defaults, strong unresolved failures, typeless kallsyms resolution, ambiguous symbols, typed ksym/kfunc compatibility, module BTF lookup, and module fd-array indexing.
- CO-RE tests for candidate search in vmlinux and modules, custom target BTF, flavor suffix matching, type compatibility/matching, skipped eliminated weak subprogram relocations, gen-loader relocation recording, and verifier-log fixup for failed guarded CO-RE.
- Relocation tests for map loads, map-value data offsets, arena offset placement, subprogram calls, pseudo-function addresses, kfunc calls, weak unresolved kfunc poison, jump table instruction-array maps, BTF func/line info offset adjustment, recursive subprogram graphs, per-main subprogram ordering, and exception callback declaration tags.
- Program load tests for missing program type, struct_ops program not referenced, expected attach type fallback, sleepable/XDP frags/USDT preload flags, BTF attach-target resolution, verifier log retry and growth, rodata map binding, probe-read helper fallback, BPF token use, and gen-loader output.
- Pinning tests for bpffs validation, missing paths, preloaded state checks, map pin-path conflicts, reuse of compatible and incompatible pinned maps, auto-pin race retry on `EEXIST`, object-level partial pin unwind, and unpin behavior across direct and derived paths.

## Cross-Chunk Notes

The source file continues beyond this chunk. This document covers the loader lifecycle up to the start of `bpf_object__unpin()`. Reconciliation should merge it with later chunks for the rest of public APIs, attachment helpers, buffer handling, introspection accessors, and full close/destruction behavior.
