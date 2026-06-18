# Research: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006586`: lines 1-9443, `Docs/researches/chunks/subset-b-006586_research.md`
- `subset-b-006587`: lines 9444-14771, `Docs/researches/chunks/subset-b-006587_research.md`

## Chunk Research

### subset-b-006586: lines 1-9443

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

### subset-b-006587: lines 9444-14771

# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf.c lines 9444-14771

## Scope

This chunk covers the tail half of the tools-side `libbpf.c` implementation bundled under `sources/distributed-fs/ceph-client`. The range starts inside `bpf_object__unpin()` and then covers object teardown, public object/program/map accessors and mutators, section-definition dispatch, BTF attach-target lookup, map operation wrappers, `bpf_link` lifecycle and attach helpers, probe/tracepoint/cgroup/network/iterator/struct_ops attachment, perf-buffer consumption, CPU mask parsing, and BPF skeleton/subskeleton lifecycle helpers.

The code is generic libbpf infrastructure, not Ceph-specific filesystem logic. Its importance to this tree is that any in-tree BPF tooling built from this copy gets its object lifetime, loading/attachment behavior, map manipulation, perf-buffer event delivery, and skeleton behavior from this implementation.

## Purpose

The chunk provides the high-level user-space API surface that turns opened BPF objects into loaded programs, attached links, usable maps, perf event consumers, and generated skeleton handles. It bridges ELF/BTF metadata and `SEC()` section naming conventions to concrete kernel operations such as `bpf_prog_load()`, `bpf_link_create()`, `bpf_map_update_elem()`, `perf_event_open()`, tracefs probe registration, and bpffs pinning.

It also centralizes many state-transition rules. Program and map definitions can be changed before load or map creation but become immutable after kernel objects exist. Link objects own detach/close behavior unless explicitly disconnected. Skeleton helpers populate generated C structs with libbpf object pointers, mmap addresses, and link slots so callers can use generated BPF skeletons without manually resolving every map and program.

## Important APIs, Types, and Functions

Object and map teardown is handled by `bpf_map__destroy()` and `bpf_object__close()`. Map destruction recursively frees inner-map templates, initial slots, mmaped data, struct_ops backing data, names, pin paths, and map FDs. Object close performs post-load cleanup, frees the USDT manager, generated loader, ELF state, BTF/BTF.ext objects, maps, extern descriptors, programs, feature cache, token path/FD, arena data, jump table data, and jump-table map FDs.

Object accessors include `bpf_object__name()`, `bpf_object__kversion()`, `bpf_object__token_fd()`, `bpf_object__btf()`, `bpf_object__btf_fd()`, `bpf_object__set_kversion()`, and `bpf_object__gen_loader()`. `bpf_object__gen_loader()` allocates a `struct bpf_gen`, records caller options, and tracks cross-endian generation.

Program APIs include iteration (`bpf_object__next_program()`, `bpf_object__prev_program()`), name/section/autoload/autoattach accessors, instruction access and replacement, FD/type/expected attach type/flags/log buffer accessors, BTF func/line info accessors, and `bpf_program__clone()`. Mutators such as `bpf_program__set_autoload()`, `bpf_program__set_type()`, `bpf_program__set_expected_attach_type()`, `bpf_program__set_flags()`, `bpf_program__set_log_level()`, and `bpf_program__set_log_buf()` reject changes after the object is loaded. `bpf_program__clone()` loads another copy of an already prepared program, merging caller-provided load options with program/object defaults and intentionally avoiding object-state mutations such as RODATA map binding.

Section dispatch is built around `struct bpf_sec_def`, the `SEC_DEF()` macro, the built-in `section_defs[]` table, custom handler globals, and `libbpf_register_prog_handler()` / `libbpf_unregister_prog_handler()`. Built-in section families cover socket filters, reuseport, kprobes, uprobes, syscall probes, USDT, tc/tcx/netkit, tracepoints, raw tracepoints, BTF tracing, LSM, iterators, syscall, XDP, perf events, LWT, cgroup, sockmap/sk_msg/sk_lookup, lirc, flow dissector, struct_ops, and netfilter. `sec_def_matches()` implements exact, `type/`, and `type+` matching; `find_sec_def()` prefers custom handlers, then built-ins, then an optional fallback handler.

Type-name helpers include `libbpf_prog_type_by_name()`, `libbpf_attach_type_by_name()`, and string conversion functions for attach, link, map, and program types. BTF attach resolution is handled by `btf_get_kernel_prefix_kind()`, `find_attach_btf_id()`, `libbpf_find_vmlinux_btf_id()`, `libbpf_find_prog_btf_id()`, `find_kernel_btf_id()`, and `libbpf_find_attach_btf_id()`. These functions map attach names to vmlinux, module, or target-program BTF type IDs, with generated-loader handling recording deferred attach targets.

Struct_ops support in this range includes `find_struct_ops_map_by_offset()`, `bpf_object__collect_st_ops_relos()`, `bpf_map__attach_struct_ops()`, `bpf_link__update_map()`, and `bpf_program__assoc_struct_ops()`. Relocation collection maps ELF relocations in struct_ops data to `struct bpf_program *` entries and shadow data. Attachment writes prepared kernel struct_ops data to map key zero and, when `BPF_F_LINK` is used, creates a real `BPF_STRUCT_OPS` link.

Map APIs include FD/name/type/flag/extra/NUMA/key-size/value-size/BTF-ID/initial-value/internal/ifindex accessors and mutators, inner-map FD configuration, exclusive-program configuration, map iteration and lookup by name, and typed wrappers for lookup, update, delete, lookup-and-delete, and get-next-key. `map_btf_datasec_resize()` adjusts BTF datasec and trailing array metadata when resizing an mmaped array map. `validate_map_op()` protects public map operations with created-map checks and key/value-size validation, including per-CPU map value sizing and `BPF_F_CPU` / `BPF_F_ALL_CPUS` handling.

Link APIs include `libbpf_get_error()`, `bpf_link__update_program()`, `bpf_link__disconnect()`, `bpf_link__destroy()`, `bpf_link__fd()`, `bpf_link__pin_path()`, `bpf_link__open()`, `bpf_link__detach()`, `bpf_link__pin()`, and `bpf_link__unpin()`. Link implementations use detach/dealloc callbacks to abstract perf-event links, fd-backed kernel links, bpffs-pinned links, and struct_ops pseudo-links.

Attachment helpers cover a broad set of program types. Perf-event attachment uses `bpf_program__attach_perf_event_opts()` and can choose real BPF links or legacy `PERF_EVENT_IOC_SET_BPF`. Kprobe and uprobe attachment support modern perf event source PMUs, explicit attach modes, legacy tracefs event registration, cookies, return probes, offsets, syscall-wrapper naming, and generated auto-attach from `SEC()` strings. Multi-kprobes and multi-uprobes use `bpf_link_create()` with symbol/address arrays, glob pattern resolution, optional uniqueness checks, cookies, sessions, and return-probe flags.

The probe support code depends on helpers for tracefs/debugfs paths, event ID parsing, syscall architecture prefixes, glob matching, `available_filter_functions` or `available_filter_functions_addrs` parsing, kallsyms fallback, binary path resolution, ELF symbol offset resolution, and archive member handling for uncompressed ZIP/APK-style files.

Other attach APIs include USDT (`bpf_program__attach_usdt()` and `attach_usdt()`), tracepoints, raw tracepoints, BTF tracing/LSM/fentry/fexit/fmod_ret/freplace, cgroup, netns, sockmap, XDP, cgroup options, TCX, netkit, iterators, netfilter, and generic `bpf_program__attach()`. `bpf_program__set_attach_target()` configures attach BTF IDs for freplace/tracing-style programs before load.

Perf-buffer support defines `struct perf_buffer_params`, `struct perf_cpu_buf`, and `struct perf_buffer`, plus `perf_buffer__new()`, `perf_buffer__new_raw()`, `perf_buffer__free()`, `perf_buffer__poll()`, `perf_buffer__consume()`, per-buffer consume/accessor helpers, and the internal `perf_event_read_simple()` ring parser. It opens one perf event per selected CPU, mmaps ring buffers, stores FDs into a `BPF_MAP_TYPE_PERF_EVENT_ARRAY`, adds FDs to epoll, dispatches raw events or higher-level sample/lost callbacks, and cleans up map slots and FDs on free.

CPU helpers include `parse_cpu_mask_str()`, `parse_cpu_mask_file()`, and `libbpf_num_possible_cpus()`. Skeleton helpers include `populate_skeleton_maps()`, `populate_skeleton_progs()`, `bpf_object__open_skeleton()`, `bpf_object__open_subskeleton()`, `bpf_object__destroy_subskeleton()`, `bpf_object__load_skeleton()`, `bpf_object__attach_skeleton()`, `bpf_object__detach_skeleton()`, and `bpf_object__destroy_skeleton()`.

## Control Flow

Object lifetime flows from open/prepare/load in earlier code into this chunk's close path. `bpf_object__close()` is defensive against partially prepared objects by invoking `bpf_object_post_load_cleanup()` before freeing resources that normal load completion would otherwise release. It then unloads kernel programs/maps, frees metadata, destroys each map, exits each program, closes token and jump-table FDs, and finally frees the object.

Program cloning starts with a prepared original program. `bpf_program__clone()` validates options, fills a `bpf_prog_load_opts` structure from caller values or program/object defaults, conditionally supplies BTF func/line records when supported, allows section-specific prepare hooks to adjust attach fields, reapplies caller attach overrides, and calls `bpf_prog_load()`.

Section matching and auto-attach flow is table driven. During object initialization, a program's `SEC()` name is mapped to a `bpf_sec_def`. Later, skeleton or explicit attach code calls the definition's `prog_attach_fn`. Some functions intentionally return success with `*link == NULL` when a section is syntactically valid but lacks enough target information for auto-attach, such as bare `SEC("kprobe")` or `SEC("uprobe")`.

Probe attachment generally follows this pattern: validate options and loaded program FD, resolve target identity from section strings or explicit arguments, choose modern or legacy attach mode, create a perf event or BPF link, attach the BPF program, enable the perf event if needed, and return a `bpf_link` with detach/dealloc callbacks. Legacy kprobe/uprobe paths append events to tracefs, open the generated tracepoint perf event, and remove the tracefs event during detach or error cleanup.

Multi-kprobe attachment either passes an exact symbol name directly to the kernel or resolves a wildcard pattern to addresses through tracefs and kallsyms. Multi-uprobe attachment resolves explicit symbol names or function patterns to ELF offsets, then calls `bpf_link_create()` with path, offset arrays, optional ref-counter offsets, optional cookies, and PID scoping.

Map operation wrappers flow through `validate_map_op()` before invoking raw BPF syscalls. This catches uncreated maps, key-size mismatches, missing FDs, regular value-size mismatches, and per-CPU value-size rules before the kernel call. The wrappers then call the corresponding `bpf_map_*` syscall wrapper.

Perf-buffer creation verifies `page_cnt` is a nonzero power of two, performs a best-effort map-type check, creates an epoll instance, determines CPU count, allocates buffer/event arrays, reads online CPUs, opens and mmaps per-CPU perf events, stores each perf FD into the BPF map, and registers each FD with epoll. Polling waits on epoll and processes records from ready CPU buffers. Consuming skips epoll and directly drains one or all buffers.

Skeleton flow starts by opening an embedded object from `s->data`, populating generated map/program pointers by name, loading the object, refreshing mmap pointers after load, and auto-attaching programs or struct_ops maps that are marked for autoattach. Destruction always detaches generated links, closes the object, and frees generated arrays.

## State and Persistence Behavior

This code owns both user-space state and kernel object references. `struct bpf_object`, `struct bpf_map`, `struct bpf_program`, `struct bpf_link`, and `struct perf_buffer` contain heap pointers and FDs that must be released exactly once through the matching close/free/destroy helpers. `bpf_link__disconnect()` changes ownership semantics by preventing destruction from detaching the underlying kernel resource.

Program and map mutators are state-gated. Program type, attach type, flags, instructions, autoload, log buffer, and kversion changes are rejected after load or preparation boundaries. Map type, flags, extra, NUMA node, key/value size, ifindex, inner-map FD, and exclusive program are rejected after map creation. These checks prevent divergence between libbpf's cached metadata and kernel-created objects.

Pinning state is represented by `pin_path` strings on maps and links, with filesystem persistence in bpffs managed through `bpf_obj_pin()`, `bpf_obj_get()`, and `unlink()`. Opened pinned links are represented as `bpf_link` objects whose detach callback closes the FD.

Perf-buffer state persists until `perf_buffer__free()`: per-CPU perf FDs are stored in the perf-event-array map, ring buffers remain mmaped, and epoll tracks readiness. Freeing deletes the map entries, disables and closes perf events, unmaps memory, closes epoll, and frees callback storage.

CPU possible-count caching persists in a static `cpus` variable populated from `/sys/devices/system/cpu/possible` with `READ_ONCE()` / `WRITE_ONCE()`. Online CPU masks are read at perf-buffer creation time and are not dynamically updated.

Skeleton state is split between generated caller-owned `struct bpf_object_skeleton` fields and libbpf-owned object/link resources. `open_skeleton()` fills map/program pointers; `load_skeleton()` fills mmap addresses; `attach_skeleton()` fills link pointers; `detach_skeleton()` clears links to `NULL`.

## Dependencies and Integration Points

The chunk depends heavily on Linux BPF syscalls and libbpf internal wrappers: `bpf_prog_load()`, `bpf_link_create()`, `bpf_link_update()`, `bpf_link_detach()`, `bpf_obj_get()`, `bpf_obj_pin()`, `bpf_map_*()` operations, `bpf_prog_get_info_by_fd()`, `bpf_map_get_info_by_fd()`, `bpf_raw_tracepoint_open_opts()`, and `bpf_prog_assoc_struct_ops()`.

BTF integration uses `btf__load_vmlinux_btf()`, `btf_load_from_kernel()`, `btf__find_by_name_kind()`, `btf__type_by_id()`, datasec/array/member helpers, module BTF loading, and object-local `btf_vmlinux` / module BTF caches. Attach-target resolution connects section metadata to kernel, module, or target-program BTF IDs.

Probe and trace attachment integrate with `perf_event_open()`, `ioctl(PERF_EVENT_IOC_SET_BPF/ENABLE/DISABLE)`, `/sys/bus/event_source/devices/{kprobe,uprobe}`, tracefs/debugfs `kprobe_events`, `uprobe_events`, `available_filter_functions`, `available_filter_functions_addrs`, tracepoint event ID files, kallsyms parsing, ELF symbol resolution, ZIP archive parsing, environment path lookup, and architecture-specific syscall naming.

Network and cgroup attachment helpers integrate with kernel link types for cgroup, netns, sockmap, XDP, TCX, netkit, netfilter, and iterator targets. Relative attach options and expected revisions are forwarded through `bpf_link_create_opts`.

USDT attachment integrates with a lazily allocated `usdt_manager` stored on the object. The manager is freed by `bpf_object__close()`, so USDT links and object lifetime are coupled.

Generated skeleton helpers integrate with bpftool-style generated C skeleton structures: `struct bpf_object_skeleton`, `struct bpf_map_skeleton`, `struct bpf_prog_skeleton`, `struct bpf_object_subskeleton`, and `struct bpf_var_skeleton`. They rely on map/program names and BTF datasec variable metadata remaining consistent with generated code.

## Risks and Edge Cases

The chunk starts inside `bpf_object__unpin()`, so full-file reconciliation should combine it with the preceding chunk for the complete pin/unpin story.

Lifetime bugs are high impact. Missing detach callbacks, double destruction, forgetting to clear skeleton link pointers, or closing a perf FD still used as a link FD can detach programs unexpectedly or leak kernel resources. The perf link detach path has special handling for `perf_event_fd != link->fd` and for legacy tracefs event cleanup.

State gating must remain strict. Allowing program or map metadata changes after load/map creation can make libbpf's cached type, size, BTF, or attach metadata inconsistent with kernel objects. Conversely, overly strict checks can break callers that legitimately configure objects between open, prepare, and load.

Section matching is order sensitive. Custom definitions override built-ins, built-ins rely on longest/specific entries appearing before broader aliases, and fallback handlers catch all unmatched sections. Incorrect matching can load a program with the wrong type, expected attach type, sleepable flag, or auto-attach handler.

Probe attachment has many environment-sensitive failure modes: missing tracefs/debugfs, unsupported kprobe/uprobe PMUs, kernels without perf-link support, unavailable syscall wrapper naming, unresolved symbols, duplicate wildcard matches when uniqueness is requested, stripped or LTO-renamed symbols, compressed archive members, missing execute/read permissions, and unsupported reference counters in legacy uprobes.

Multi-probe option validation is subtle. Pattern mode is mutually exclusive with explicit arrays; address and symbol arrays are mutually exclusive; `cnt` must be nonzero for explicit arrays; return-probe and session modes are mutually exclusive. Violating these combinations should fail early rather than passing ambiguous options to the kernel.

Perf-buffer parsing assumes valid perf ring records. Wrapped records are copied into a temporary buffer, and `page_cnt` must be a power of two. Bad map type, offline CPUs, stale online masks, insufficient map entries, epoll registration failures, or malformed record types all produce errors or skipped buffers.

`parse_cpu_mask_str()` reallocates to `end + 1` bytes for a `bool` mask and uses range filling based on previous mask size. It expects monotonically sensible CPU mask ranges from sysfs; malformed, descending, negative, oversized, or empty masks produce errors.

Map value resizing for mmaped array maps depends on BTF datasec shape: the map value type must be a datasec, have at least one var, and end with an array whose element size divides the requested new size. If BTF adjustment fails after mmap resizing, the code clears map BTF key/value IDs to avoid stale metadata.

Skeleton helpers depend on generated skeleton ABI sizes. Older skeletons without map link fields skip struct_ops map auto-attachment. Subskeleton variable population does not report an error when a requested variable name is not found after scanning a datasec, so consumers must be aware that unresolved addresses could remain unchanged.

## Test Signals

Useful validation signals for this chunk include:

- Object lifecycle tests that open, prepare-only, load, unload, close, and error-close objects with programs, maps, externs, BTF, tokens, arena data, jump tables, USDT manager state, and mmaped map data.
- Program API tests for pre-load and post-load mutator behavior, program iteration skipping subprograms, instruction replacement including zero-length replacement, log buffer validation, func/line info access, and clone loading with caller option overrides.
- Section resolution tests for all built-in `SEC()` families, exact versus `+` versus trailing-slash matching, custom handler registration/unregistration, fallback handlers, and type/attach-name string helpers.
- BTF attach tests for vmlinux, module-qualified names, target-program BTF IDs, freplace targets, generated-loader deferred attach recording, missing BTF, missing symbols, and token-FD propagation.
- Map API tests for map FD/name lookup, internal real-name handling for `.data.*`/`.rodata.*`, resize of mmaped arrays with BTF datasec metadata, initial value sizing, inner-map FD replacement, exclusive-program validation, and typed map operation size checks including per-CPU maps and CPU flags.
- Link lifecycle tests for open/pin/unpin/destroy/disconnect/update-program, bpffs path errors, close-only detached links, and legacy perf links that must remove tracefs kprobe/uprobe events.
- Kprobe/uprobe tests covering modern PMU attach, forced perf attach, forced link attach, forced legacy attach, return probes, offsets, cookies, syscall wrapper detection, auto-attach section parsing, missing targets, wildcard multi-kprobe resolution, unique-match failures, and session mode.
- Uprobe path and symbol tests for PATH/LD_LIBRARY_PATH resolution, architecture library fallback paths, ELF symbol offsets, function patterns, explicit offsets, archive member offsets, compressed archive rejection, PID scoping, and ref-counter offset handling.
- Tracepoint/raw tracepoint/BTF tracing/LSM/freplace/iterator/cgroup/netns/sockmap/XDP/TCX/netkit/netfilter attach tests for loaded-FD validation, expected attach type, relative attach options, revision/options propagation, and unsupported kernel behavior.
- Struct_ops tests for relocation collection into function-pointer members, non-static or wrong-type program rejection, map update idempotence with `-EBUSY`, `BPF_F_LINK` and non-link attach modes, link map update, and associate-struct-ops errors.
- Perf-buffer tests for invalid page counts, wrong map types, CPU subset options, offline CPU skipping, map slot updates, epoll readiness, wrapped record copying, raw event callback precedence, sample/lost callbacks, consume without polling, buffer FD/accessor bounds, and cleanup deleting perf-event-array slots.
- CPU mask tests for single CPUs, ranges, comma/newline separation, empty masks, invalid ranges, descending ranges, malformed strings, too-large sysfs file reads, and cached possible CPU counts.
- Skeleton tests for open/load/attach/detach/destroy, missing generated map/program names, mmap pointer refresh after load including arena offset handling, autoattach disabled programs/maps, manually prefilled links, old skeleton map sizes, subskeleton BTF datasec variable lookup, and cleanup after partial failures.

## Cross-Chunk Notes

Earlier chunks for the same file contain object opening, ELF/BTF collection, relocation, map creation, program loading, and most pin/unpin definitions. This chunk should be reconciled with those earlier ranges because many functions here call helpers defined earlier, especially `bpf_object_post_load_cleanup()`, `bpf_object_unload()`, `bpf_map_mmap_sz()`, `kernel_supports()`, `load_module_btfs()`, ELF symbol resolution helpers, and section setup during object initialization.

The final per-file report should treat this range as libbpf's public API and runtime integration tail: it is where prepared object metadata becomes attached kernel links, map operations, perf-buffer consumers, and generated skeleton state.
