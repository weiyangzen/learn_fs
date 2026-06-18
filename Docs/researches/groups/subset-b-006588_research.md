<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf.h

## Purpose
This is the main public libbpf API header bundled under the Ceph client tool tree. It declares the user-facing ABI for opening, preparing, loading, pinning, querying, and attaching eBPF ELF objects, programs, maps, links, XDP/TC hooks, ring/perf buffers, skeletons, BPF linker operations, custom `SEC()` handlers, and single-program cloning.

## APIs, Types, and Functions
Version and diagnostics APIs include `libbpf_major_version()`, `libbpf_minor_version()`, `libbpf_version_string()`, `libbpf_strerror()`, enum-to-string helpers, `enum libbpf_errno`, `enum libbpf_print_level`, `libbpf_print_fn_t`, and `libbpf_set_print()`. Object APIs revolve around opaque `struct bpf_object`, `struct bpf_object_open_opts`, `bpf_object__open*()`, `bpf_object__prepare()`, `bpf_object__load()`, `bpf_object__close()`, map/program pinning helpers, object name/kernel-version/token/BTF accessors, program lookup, and program/attach type resolution.

Program APIs expose iteration, names, section names, autoload/autoattach switches, mutable instruction access through `bpf_program__insns()`, `bpf_program__set_insns()`, and `bpf_program__insn_cnt()`, FD/pin/unload accessors, and a large attach surface for perf events, kprobes, uprobes, syscall probes, USDT, tracepoints, raw tracepoints, tracing, LSM, cgroup, netns, sockmap, XDP, freplace, netfilter, TCX, netkit, cgroup options, iterators, and struct-ops association. Map APIs include lookup, iteration, autocreate/autoattach, FD reuse, map metadata setters, initial values, internal-map detection, pin/unpin, inner-map configuration, typed element operations, next-key iteration, and exclusive-program binding. Networking APIs define XDP attach/query options and TC hook/opts structures. Buffer APIs define ring buffer, user ring buffer, and perf buffer constructors and consumers. Loader-generation and skeleton APIs define `bpf_object_skeleton`, subskeleton, var skeleton, and `bpf_object__gen_loader()`. Linker APIs declare `struct bpf_linker`, `bpf_linker__new*()`, `bpf_linker__add_*()`, `bpf_linker__finalize()`, and `bpf_linker__free()`. Custom section handler APIs expose setup, prepare-load, and attach callbacks plus register/unregister functions. The final declared API, `bpf_program__clone()`, loads one program from a prepared object and returns a caller-owned FD.

## Control Flow, State, and Persistence
This header itself has no executable control flow, but it defines the expected lifecycle: create/open an object, tune object/program/map settings before load, optionally call `bpf_object__prepare()`, load into the kernel, attach programs or maps, persist kernel objects through bpffs pins, consume ring/perf events, and release user-space wrappers. State is carried through opaque `bpf_object`, `bpf_program`, `bpf_map`, `bpf_link`, buffer manager, skeleton, and linker instances. Persistent kernel state is explicitly created by map/program/link pinning and by attaching programs to kernel hooks; `bpf_link__disconnect()` and destroy/detach APIs split wrapper ownership from kernel attachment lifetime.

## Dependencies and Integration
The header depends on Linux UAPI `linux/bpf.h`, standard C integer/bool/size types, and local `libbpf_common.h` and `libbpf_legacy.h`. It is consumed by libbpf implementation files and by tool callers that need a stable libbpf-style C ABI. It integrates with bpffs pinning, BTF, libelf-backed object loading, `bpf()` syscalls, perf events, rtnetlink/genetlink XDP and TC operations, skeleton generation, and custom program-section dispatch.

## Risks and Test Signals
Key risks are ABI compatibility around options structs and `*_last_field` markers, correct zero-initialization of future option fields, load/attach calls used after objects are already loaded, pointer lifetime for instruction arrays and initial map values, thread-safety gaps explicitly noted for global custom handler registration, and kernel-feature drift across BPF program/map/link types. Test signals should include compile tests for header consumers, option-size forward/backward compatibility tests, object open/prepare/load/close lifecycles, pin/unpin persistence checks, representative attach/detach tests for XDP/TC/probe/link APIs, skeleton open/load/attach/destroy flows, and linker API smoke tests using small relocatable BPF objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_common.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_common.h

## Purpose
This public helper header defines common libbpf ABI annotations, deprecation machinery, lightweight macro overloading, and canonical option-struct initialization/reset helpers shared by libbpf public headers.

## APIs, Types, and Functions
The file defines `LIBBPF_API` as default symbol visibility unless already supplied, `LIBBPF_DEPRECATED()`, and `LIBBPF_DEPRECATED_SINCE()` backed by current `LIBBPF_MAJOR_VERSION` and `LIBBPF_MINOR_VERSION`. It provides preprocessor helpers `___libbpf_cat`, `___libbpf_select`, `___libbpf_nth`, `___libbpf_cnt`, and `___libbpf_overload` for argument-count dispatch. `LIBBPF_OPTS(TYPE, NAME, ...)` declares a local options struct, clears all bytes with `memset()`, sets `.sz`, and applies caller field initializers. `LIBBPF_OPTS_RESET(NAME, ...)` rebuilds an existing option variable with all bytes cleared and `.sz` reset.

## Control Flow, State, and Persistence
There is no runtime state beyond code emitted by macros at use sites. The important behavior is zeroing entire option objects, including padding, before assigning user-specified fields. This supports libbpf's convention that `.sz` defines which fields are visible to the implementation and that trailing bytes must be zero for forward compatibility.

## Dependencies and Integration
It includes `<string.h>` for `memset()` and `memcpy()` and local `libbpf_version.h` for version-gated deprecation. It is included by `libbpf.h`, `libbpf_legacy.h`, and downstream callers using libbpf option structs.

## Risks and Test Signals
Risks include compiler-specific GNU statement-expression and `typeof` usage, padding bytes not being guaranteed by all compound-literal implementations despite the explicit reset pattern, and deprecation gates needing updates as versions advance. Test signals are compile tests under supported compilers, static assertions that `.sz` is initialized, API calls with older and larger options sizes, and warnings appearing only at intended version thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_internal.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_internal.h

## Purpose
This internal libbpf header centralizes portability shims, ELF/BPF relocation constants, BTF encoding helpers, logging macros, internal object/link structures, option validation, kernel feature IDs, BTF/BTF.ext layouts, endian helpers, FD utilities, ELF symbol helpers, CO-RE interfaces, USDT interfaces, and SHA-256 declarations used by libbpf implementation files.

## APIs, Types, and Functions
Portability definitions cover Android `AT_EACCESS`, `EM_BPF`, BPF relocation numbers, `SHT_LLVM_ADDRSIG`, old-libelf `ELF_C_READ_MMAP`, and `ELF64_ST_VISIBILITY`. BTF construction macros include `BTF_INFO_ENC`, `BTF_TYPE_ENC`, `BTF_INT_ENC`, `BTF_TYPE_INT_ENC`, `BTF_MEMBER_ENC`, `BTF_PARAM_ENC`, `BTF_VAR_SECINFO_ENC`, `BTF_TYPE_FLOAT_ENC`, `BTF_TYPE_DECL_TAG_ENC`, and `BTF_TYPE_TYPE_TAG_ENC`. General helpers define `likely`, `unlikely`, `min`, `max`, `offsetofend`, `__alias`, `str_has_pfx()`, and `str_has_sfx()`.

Symbol-version macros `DEFAULT_VERSION` and `COMPAT_VERSION` adapt between shared-library symver attributes, assembler `.symver`, and static aliases. Logging routes `pr_warn`, `pr_info`, and `pr_debug` through `libbpf_print()`. `struct bpf_link` stores detach/dealloc callbacks, optional pin path, FD, and disconnected state. Memory/string helpers include `libbpf_reallocarray()` with overflow checks and `libbpf_strlcpy()`. Options macros use `libbpf_validate_opts()`, `OPTS_VALID`, `OPTS_HAS`, `OPTS_GET`, `OPTS_SET`, and `OPTS_ZEROED`.

Kernel-feature state is represented by `enum kern_feature_id`, `enum kern_feature_result`, and `struct kern_feature_cache`. BTF APIs declared here include type lookup, kind strings, modifier skipping, BTF relocation/base setup, map definition parsing, raw BTF loading, BTF kernel loading/fetching, attach-prefix lookup, BTF.ext iterators, byte-swappers for func/line/core relo records, `btf_field_iter`, and visitor functions for type IDs and string offsets. Error helpers include `libbpf_err()`, `libbpf_err_errno()`, `libbpf_err_ptr()`, and `libbpf_ptr()`. FD helpers include `dup_good_fd()`, `ensure_good_fd()`, `sys_dup3()`, `sys_memfd_create()`, and `reuse_fd()`. The header also declares CO-RE candidate helpers, USDT manager helpers, `is_pow_of_2()`, `ror32()`, `sys_bpf_prog_load()`, glob matching, ELF offset resolvers/open/close helpers, `probe_fd()`, and `libbpf_sha256()`.

## Control Flow, State, and Persistence
Most logic is inline utility behavior. Options validation rejects too-small `.sz` values or nonzero bytes beyond known fields. Error helpers normalize libbpf's convention of returning negative errors while setting `errno` for public APIs. FD helpers deliberately move FDs out of the stdio range, duplicate FDs with close-on-exec, and close temporary FDs after reuse. `struct kern_feature_cache` persists per-object feature probe results and token FD. `struct btf_ext` stores parsed and possibly byte-swapped BTF.ext sections plus record-size metadata. `struct bpf_link` persists ownership state for attached or pinned kernel links.

## Dependencies and Integration
The header depends on libc allocation/FD/syscall headers, libelf, Linux error helpers, and local `relo_core.h`, `libbpf.h`, and `btf.h`. It is included throughout libbpf implementation files such as object loading, BTF, linker, netlink, probes, and utilities. Integration points include ELF parsing, BTF and CO-RE relocation, `bpf()` syscalls, USDT attachment, feature probing, and public API error/log handling.

## Risks and Test Signals
Risks include inline ABI assumptions about struct layouts, integer overflow in allocation and alignment arithmetic, GNU/compiler-specific poison/symver behavior, stale kernel feature IDs, misuse of `OPTS_GET` on invalid option objects, FD ownership confusion in `ensure_good_fd()`/`reuse_fd()`, and byte-order handling for BPF instructions and BTF.ext records. Test signals should cover option compatibility, realloc overflow, FD duplication/reuse semantics, BTF.ext iteration across record sizes, endian byte-swapping, public API errno behavior, feature-cache behavior with token FDs, and builds across shared/static and Android/libelf variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_legacy.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_legacy.h

## Purpose
This public header preserves legacy or discouraged libbpf APIs so applications prepared for or migrated through libbpf 1.0 can still compile without adopting newer names and behavior immediately.

## APIs, Types, and Functions
`enum libbpf_strict_mode` documents historical strict-mode bits including clean pointers, direct errors, strict section names, no object list, automatic memlock rlimit bumping, and strict map definitions. In libbpf 1.0+ `libbpf_set_strict_mode()` is intentionally retained but has no effect. `libbpf_get_error()` is retained for old ERR_PTR-style pointer error handling, although modern libbpf returns `NULL` and uses `errno`. `DECLARE_LIBBPF_OPTS` aliases `LIBBPF_OPTS`. Discouraged compatibility APIs include `libbpf_find_kernel_btf()`, `bpf_program__get_type()`, `bpf_program__get_expected_attach_type()`, `bpf_map__get_pin_path()`, `btf__get_raw_data()`, and `btf_ext__get_raw_data()`.

## Control Flow, State, and Persistence
This header only declares compatibility entry points. The important state behavior is semantic: strict-mode flags no longer change global runtime behavior, and `libbpf_get_error(NULL)` is only reliable if `errno` still reflects the preceding libbpf call. The discouraged accessor APIs expose existing object/program/map/BTF state without owning it.

## Dependencies and Integration
It includes Linux BPF UAPI types, C scalar headers, and `libbpf_common.h`, and is included by `libbpf.h`. It integrates with older libbpf callers and migration code that has not switched to modern names or direct errno checks.

## Risks and Test Signals
Risks include callers believing strict mode still toggles behavior, `errno` being overwritten before `libbpf_get_error()`, and new code copying discouraged naming patterns. Test signals are compile compatibility for legacy callers, runtime checks that `libbpf_set_strict_mode()` is harmless, and error-path tests documenting modern `NULL` plus `errno` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_legacy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_probes.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_probes.c

## Purpose
This implementation probes host-kernel BPF capabilities by attempting small BPF program loads, map creations, and BTF loads. It also derives kernel version codes for kernels where `uname()` does not match the version expected by BPF program loading.

## APIs, Types, and Functions
Kernel version helpers are `get_ubuntu_kernel_version()`, `get_debian_kernel_version()`, and public internal `get_kernel_version()`. Program probing is built around `probe_prog_load()` and exported as `libbpf_probe_bpf_prog_type()` and `libbpf_probe_bpf_helper()`. Raw BTF helpers `libbpf__load_raw_btf_hdr()` and `libbpf__load_raw_btf()` construct a BTF blob and call `bpf_btf_load()`. `load_local_storage_btf()` creates a minimal BTF schema for local-storage map probes. `probe_map_create()` covers map-type-specific key/value/max_entries/options setup and is exported as `libbpf_probe_bpf_map_type()`.

## Control Flow, State, and Persistence
`get_kernel_version()` first tries `/proc/version_signature` for Ubuntu, then Debian `utsname.version`, then `utsname.release`, returning a `KERNEL_VERSION()` code or zero. `probe_prog_load()` builds minimal instructions, configures expected attach type or special expected failure cases for tracing, LSM, EXT, syscall, struct_ops, and kprobes, calls `bpf_prog_load()`, closes any successful FD, and returns `1` for supported, `0` for unsupported, or a negative error for unsupported input. `probe_map_create()` selects valid dimensions and flags per map type, creates inner maps or temporary BTF where required, calls `bpf_map_create()`, closes all created FDs, and treats selected expected errors as support signals. `libbpf_probe_bpf_helper()` loads a two-instruction program calling the helper and interprets verifier logs containing invalid/unknown helper messages as lack of support; other verifier errors are treated as likely support.

State is transient: FDs for programs, maps, inner maps, and BTF are closed before return. The only external state read is `/proc/version_signature` and `uname()`. Probes can consume kernel resources temporarily and rely on privileges/capabilities.

## Dependencies and Integration
The file depends on `bpf.h` syscall wrappers, `libbpf.h`, `libbpf_internal.h`, Linux BTF/filter/kernel/version headers, libc file and uname APIs, and network interface definitions. It feeds internal feature checks and public probe APIs declared in `libbpf.h`.

## Risks and Test Signals
Risks include false negatives without CAP_BPF/CAP_SYS_ADMIN or sufficient memlock, kernel verifier message changes affecting helper detection, distro version parsing drift, expected-error matching for special program/map types, temporary BTF layout compatibility, and probes failing under constrained containers. Test signals include controlled unit tests for distro version parsing, integration tests on kernels with known map/prog/helper support matrices, verifier-log pattern tests, FD leak checks, and privilege-denied behavior distinguishing unsupported features from execution failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_probes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_utils.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_utils.c

## Purpose
This utility implementation provides libbpf error string conversion and an internal SHA-256 implementation used by libbpf components that need deterministic hashing without external crypto dependencies.

## APIs, Types, and Functions
Error APIs are `libbpf_strerror()` and internal `libbpf_errstr()`. Static data includes `libbpf_strerror_table[]` mapping custom `enum libbpf_errno` values to messages. SHA-256 support includes unaligned big-endian helpers `get_unaligned_be32()` and `put_unaligned_be32()`, compression constants `sha256_K[]`, boolean/rotation macros, `sha256_blocks()`, and public internal `libbpf_sha256()`.

## Control Flow, State, and Persistence
`libbpf_strerror()` validates the destination buffer, normalizes positive and negative errors, delegates ordinary errno values to `strerror_r()`, maps libbpf private errors through `libbpf_strerror_table`, and returns `-ERANGE` if the formatted message was truncated or `-ENOENT` for unknown libbpf error numbers. It always NUL-terminates nonempty output buffers. `libbpf_errstr()` returns constant strings for common negative errno values or a thread-local numeric buffer for unknown values. `libbpf_sha256()` initializes the SHA-256 state, processes whole 64-byte blocks, pads the final one or two blocks with the bit count, compresses them, and writes a 32-byte big-endian digest.

Persistent state is limited to the thread-local fallback buffer in `libbpf_errstr()`. SHA-256 state is stack-local and deterministic.

## Dependencies and Integration
The file depends on libc formatting/string errors, Linux endian/kernel macros such as `ARRAY_SIZE` and `roundup`, local public and internal libbpf headers, and `ror32()` from `libbpf_internal.h`. Error conversion backs public diagnostics and internal logging. SHA-256 is declared in the internal header and can be used by loader/linker code for stable content hashes.

## Risks and Test Signals
Risks include platform differences in `strerror_r()` return semantics, missing table entries for new `enum libbpf_errno` values, the small thread-local numeric buffer in `libbpf_errstr()`, pointer arithmetic on `const void *` relying on compiler extensions, and SHA-256 correctness for boundary lengths. Test signals should include ordinary errno and private errno conversion, truncation behavior, unknown error handling, thread-local fallback isolation, and SHA-256 known-answer vectors for empty input, one block, 55/56/57-byte padding boundaries, and multi-block input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_version.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_version.h

## Purpose
This tiny public header defines the vendored libbpf major and minor version macros used by compile-time deprecation and compatibility logic.

## APIs, Types, and Functions
It defines `LIBBPF_MAJOR_VERSION` as `1` and `LIBBPF_MINOR_VERSION` as `8`. It has no functions or types.

## Control Flow, State, and Persistence
There is no runtime behavior or state. The version macros affect preprocessing, especially `LIBBPF_DEPRECATED_SINCE()` in `libbpf_common.h`, and may be used by consumers for compile-time feature checks.

## Dependencies and Integration
It is included by `libbpf_common.h`, which is included by the public libbpf headers. It must stay synchronized with the vendored libbpf implementation and exported version functions.

## Risks and Test Signals
Risks are version skew between this header, compiled implementation functions, symbol versions, and documentation. Test signals are compile-time checks in consumers, runtime comparison against `libbpf_major_version()`, `libbpf_minor_version()`, and `libbpf_version_string()`, and packaging checks when vendoring a new libbpf release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/libbpf_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/linker.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/linker.c

## Purpose
This file implements libbpf's static linker for BPF relocatable ELF objects. It combines multiple input BPF object files or buffers into one output ELF, merging compatible data/code sections, symbols, relocations, BTF, and `.BTF.ext` metadata while resolving global and extern symbols.

## APIs, Types, and Functions
Public APIs are `bpf_linker__new()`, `bpf_linker__new_fd()`, `bpf_linker__add_file()`, `bpf_linker__add_fd()`, `bpf_linker__add_buf()`, `bpf_linker__finalize()`, and `bpf_linker__free()`. Core state types include `struct src_sec`, `struct src_obj`, `struct btf_ext_sec_data`, `struct glob_sym`, `struct dst_sec`, and `struct bpf_linker`.

Initialization helpers include `init_output_elf()`, `add_dst_sec()`, `add_new_sym()`, and `emit_elf_data_sec()`. Input loading and validation is handled by `linker_load_obj_file()`, `is_ignored_sec()`, `linker_sanity_check_elf()`, `linker_sanity_check_elf_symtab()`, `linker_sanity_check_elf_relos()`, `linker_sanity_check_btf()`, `linker_sanity_check_btf_ext()`, `check_btf_type_id()`, and `check_btf_str_off()`. Section merging uses `init_sec()`, `find_dst_sec_by_name()`, `secs_match()`, `sec_content_is_same()`, `extend_sec()`, `linker_append_sec_data()`, and endian helpers `is_exec_sec()`/`exec_sec_bswap()`. Symbol and relocation handling uses `linker_append_elf_syms()`, `linker_append_elf_sym()`, `find_glob_sym()`, `add_glob_sym()`, `glob_sym_btf_matches()`, `map_defs_match()`, `glob_map_defs_match()`, `glob_syms_match()`, `find_glob_sym_btf()`, `complete_extern_btf_info()`, `sym_update_*()`, `linker_append_elf_relos()`, and `find_sym_by_name()`. BTF logic uses `linker_fixup_btf()`, `linker_append_btf()`, `add_btf_ext_rec()`, `linker_append_btf_ext()`, `finalize_btf()`, `emit_btf_ext_data()`, and `finalize_btf_ext()`.

## Control Flow, State, and Persistence
`bpf_linker__new()` or `bpf_linker__new_fd()` initializes libelf, allocates linker state, creates or adopts the output FD, initializes an ELF header for `EM_BPF`/`ET_REL`, creates `.strtab` and `.symtab`, creates an empty BTF object, and inserts the all-zero symbol. Each `bpf_linker__add_*()` path passes an FD-backed input into `bpf_linker_add_file()`. Buffer inputs are first copied into a memfd.

For each input, `linker_load_obj_file()` parses an ELF64 BPF relocatable object, establishes output endianness from the first input, discovers sections, skips string tables, DWARF, LLVM address-signature, empty `.text`, `.BTF`, `.BTF.ext`, and BTF relocations as appropriate, parses BTF/BTF.ext sections into side structures, and validates ELF/BTF consistency. `linker_fixup_btf()` maps DATASEC types to ELF sections, creates ephemeral section shells for special BTF-only sections such as `.kconfig` and `.ksyms`, and fixes global variable offsets from ELF symbols.

Merging proceeds in stages. `linker_append_sec_data()` creates or extends output data/code/BSS sections, deduping only identical `license` and `version` sections. `extend_sec()` aligns destination size, copies bytes, records source destination offsets, and temporarily byte-swaps executable BPF instructions into host order when linking opposite-endian objects. `linker_append_elf_syms()` maps local and global symbols into the output symtab. Global symbol logic resolves externs, weak/strong definitions, visibility contamination, `.maps` definition compatibility, BTF type compatibility, and updates existing extern BTF info when a concrete definition is found. `linker_append_elf_relos()` appends relocation sections, remaps symbol indices, offsets relocation locations by appended section offsets, and adjusts calls through section symbols in executable sections.

BTF merging appends non-DATASEC types, reuses existing global VAR/FUNC BTF IDs, remaps type references, rewrites underlying VAR/FUNC types when externs resolve, and appends consolidated DATASEC var info with adjusted offsets. `.BTF.ext` merge logic appends func info, line info, and CO-RE relocation records per destination section, remapping instruction offsets, type IDs, and string offsets. `bpf_linker__finalize()` builds final DATASEC BTF types, synthesizes `.BTF.ext`, deduplicates BTF, sets BTF endianness, emits `.BTF` and `.BTF.ext` ELF sections, finalizes `.strtab`, restores executable sections to target byte order, calls `elf_update()` for layout and write, ends the ELF handle, and closes owned output FDs. `bpf_linker__free()` releases all transient allocations, BTF/BTF.ext objects, strings, raw section buffers, and optionally the output FD.

Persistent output is the final ELF written to the filename or FD. In-memory state tracks output sections, unique string table, global symbols, BTF, `.BTF.ext`, and whether the linker owns the FD.

## Dependencies and Integration
The implementation depends on libelf, Linux ELF/BTF constants, local `libbpf.h`, `btf.h`, `libbpf_internal.h`, and `strset.h`. It integrates with BTF parsing/dedup APIs, CO-RE relocation records, BPF map-definition parsing, BPF instruction endian handling, memfd syscalls, and public `bpf_linker_*` APIs declared in `libbpf.h`.

## Risks and Test Signals
Risks include malformed ELF/BTF inputs, cross-endian instruction handling, alignment and size overflow, weak/strong symbol resolution mistakes, extern BTF ambiguity, map-definition mismatch detection, BTF dedup altering expected IDs, unresolved extern semantics for library-style outputs, relocation against section symbols outside executable sections, record-size mismatches in `.BTF.ext`, and FD ownership errors. Test signals should include linking one and multiple small BPF objects, weak/strong/extern resolution cases, duplicate `license`/`version` checks, `.maps` compatibility and mismatch cases, CO-RE relocation preservation, line/func info offset adjustment, cross-endian fixtures if supported, invalid ELF/BTF rejection, memfd buffer input, finalize write validation with `llvm-objdump`/`bpftool btf dump`, and leak/FD-close checks on error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/linker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/netlink.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/netlink.c

## Purpose
This file implements libbpf's rtnetlink and generic-netlink support for XDP program attach/detach/query and TC qdisc/filter hook management.

## APIs, Types, and Functions
Public APIs are `bpf_xdp_attach()`, `bpf_xdp_detach()`, `bpf_xdp_query()`, `bpf_xdp_query_id()`, `bpf_tc_hook_create()`, `bpf_tc_hook_destroy()`, `bpf_tc_attach()`, `bpf_tc_detach()`, and `bpf_tc_query()`. Netlink helpers include `libbpf_netlink_open()`, `libbpf_netlink_close()`, `netlink_recvmsg()`, `alloc_iov()`, `libbpf_netlink_recv()`, `libbpf_netlink_send_recv()`, `parse_genl_family_id()`, and `libbpf_netlink_resolve_genl_family_id()`. XDP helpers include `__bpf_set_link_xdp_fd_replace()`, `__dump_link_nlmsg()`, `get_xdp_info()`, and `parse_xdp_features()`. TC helpers include `clsact_config()`, `qdisc_config()`, `attach_point_to_config()`, `tc_get_tcm_parent()`, `tc_qdisc_modify()`, `tc_qdisc_create_excl()`, `tc_qdisc_delete()`, `__bpf_tc_detach()`, `__get_tc_info()`, `get_tc_info()`, and `tc_add_fd_and_name()`.

## Control Flow, State, and Persistence
`libbpf_netlink_send_recv()` opens a netlink socket with `NETLINK_EXT_ACK`, binds to discover the local netlink PID, stamps the request with a time-based sequence, sends the request, and dispatches replies through `libbpf_netlink_recv()`. The receive loop peeks with `MSG_TRUNC` to size the buffer, reallocates as needed, validates PID and sequence, handles multipart responses, reports kernel extack strings through `libbpf_nla_dump_errormsg()`, and calls parser callbacks until continue/next/done.

XDP attach builds `RTM_SETLINK` with nested `IFLA_XDP` attributes for FD, flags, and optional expected old FD when replacement is requested. Detach is attach with FD `-1`. Query sends `RTM_GETLINK`, parses `IFLA_XDP` nested attributes into program IDs and attach mode, then optionally resolves the generic-netlink `netdev` family and queries feature flags plus zero-copy max segments. `bpf_xdp_query_id()` selects one program ID based on requested mode and attach mode.

TC hook creation/deletion maps ingress/egress to `clsact` qdisc or uses an explicit qdisc for `BPF_TC_QDISC`. TC attach validates hook/options, builds `RTM_NEWTFILTER` with BPF kind and nested options containing the program FD, generated name from `bpf_prog_get_info_by_fd()`, and direct-action flag, requests echo, and parses returned handle/priority/program ID. TC detach builds `RTM_DELTFILTER`, either flushing for hook destroy or deleting a specific handle/priority. TC query builds `RTM_GETTFILTER` and parses BPF filter info.

State is mostly stack-local request/response metadata. Persistent kernel state is changed by XDP attaches/detaches and TC qdisc/filter create/delete operations. Output state is written into option structs through `OPTS_SET()`.

## Dependencies and Integration
The implementation depends on Linux rtnetlink, generic netlink, netdev, pkt_cls, BPF, Ethernet protocol constants, sockets, time, local `bpf.h`, `libbpf.h`, `libbpf_internal.h`, and `nlattr.h`. It integrates public libbpf networking APIs with kernel route and generic netlink subsystems and uses `bpf_prog_get_info_by_fd()` to name TC filters.

## Risks and Test Signals
Risks include time-based sequence collisions across concurrent requests, strict PID/sequence validation rejecting unexpected multicast/unicast replies, kernel feature differences for `NETLINK_EXT_ACK` and `netdev` generic family, fixed `libbpf_nla_req` buffer size causing `-EMSGSIZE`, invalid XDP flag combinations, TC attach-point parent validation, cleanup behavior when qdisc/filter operations partially fail, and required privileges for network configuration. Test signals should include netlink unit tests for malformed responses, XDP attach/replace/detach/query on a test interface, query fallback when `netdev` family is absent, TC clsact create/attach/query/detach/destroy, custom qdisc validation, extack logging, and option-size compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/nlattr.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/nlattr.c

## Purpose
This file implements netlink attribute parsing, validation, nested parsing, and extended-ack error message extraction for libbpf's netlink code.

## APIs, Types, and Functions
Static helpers include `nla_attr_minlen[]`, `nla_next()`, `nla_ok()`, `nla_type()`, `validate_nla()`, and `nlmsg_len()`. Public internal functions are `libbpf_nla_parse()`, `libbpf_nla_parse_nested()`, and `libbpf_nla_dump_errormsg()`.

## Control Flow, State, and Persistence
`libbpf_nla_parse()` clears the caller-provided table, iterates attributes with `libbpf_nla_for_each_attr()`, ignores types above `maxtype`, validates each attribute against an optional policy, warns on duplicates while replacing the table entry with the later attribute, and returns the first validation error. `validate_nla()` derives minimum length from explicit policy or type defaults, enforces max length, and ensures string attributes end in NUL. `libbpf_nla_parse_nested()` parses the payload of a nested attribute as a new attribute stream. `libbpf_nla_dump_errormsg()` checks `NLM_F_ACK_TLVS`, accounts for capped versus uncapped embedded request length, parses `NLMSGERR_ATTR_MSG` and `NLMSGERR_ATTR_OFFS`, and logs the kernel error string when present.

The file has no persistent state except immutable minimum-length table data. All parse output is written into caller-owned arrays.

## Dependencies and Integration
It depends on Linux rtnetlink/netlink structures, local `nlattr.h` declarations, and `libbpf_internal.h` logging. `netlink.c` uses it to parse route and generic-netlink responses and extack errors.

## Risks and Test Signals
Risks include duplicate attribute replacement semantics, missing warning context, out-of-bounds calculations for malformed extended-ack messages, string policy behavior on zero-length payloads, ignoring leftover trailing bytes after the attribute loop, and accepting unknown high attributes for compatibility. Test signals should include valid and malformed attribute streams, min/max length policies, non-NUL strings, duplicates, nested parse fixtures, extack messages with and without `NLM_F_CAPPED`, and fuzzing truncated netlink payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/nlattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/nlattr.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/nlattr.h

## Purpose
This internal header defines libbpf's netlink attribute type policy model, request buffer type, iteration macros, payload accessors, and inline request-building helpers.

## APIs, Types, and Functions
It defines `LIBBPF_NLA_*` validation type constants and `LIBBPF_NLA_TYPE_MAX`, `struct libbpf_nla_policy` with type/minlen/maxlen, and `struct libbpf_nla_req`, which contains a `nlmsghdr`, a union for `ifinfomsg`, `tcmsg`, or `genlmsghdr`, and a fixed 128-byte attribute buffer. Iteration and accessor APIs include `libbpf_nla_for_each_attr`, `libbpf_nla_data()`, typed getters for u8/u16/u32/u64/string, `libbpf_nla_len()`, parser declarations, `libbpf_nla_dump_errormsg()`, `nla_data()`, `req_tail()`, `nlattr_add()`, `nlattr_begin_nested()`, and `nlattr_end_nested()`.

## Control Flow, State, and Persistence
Inline getters compute payload addresses relative to `NLA_HDRLEN` and read values directly without byte-order conversion. `nlattr_add()` checks that the aligned request length plus aligned new attribute fits in `sizeof(struct libbpf_nla_req)`, rejects mismatched data/length pairs, writes type and length, copies payload if present, and advances `nlmsg_len`. `nlattr_begin_nested()` records the current tail and adds a zero-length nested attribute with `NLA_F_NESTED`; `nlattr_end_nested()` fills its final length from the current request tail. No persistent state is maintained beyond the caller-owned request object.

## Dependencies and Integration
The header depends on standard integer/string/errno headers and Linux netlink, rtnetlink, and generic-netlink UAPI headers. It is included by `nlattr.c` and `netlink.c` to construct and parse netlink requests for XDP and TC operations.

## Risks and Test Signals
Risks include the small fixed request buffer limiting future attributes, direct unaligned typed reads on architectures sensitive to alignment, no endian conversion for netlink payload values, caller responsibility for valid nested begin/end pairing, and the deliberate `__LINUX_NETLINK_H` define potentially interacting with kernel header feature guards. Test signals should include buffer-boundary request-building tests, invalid data/length combinations, nested attribute length checks, typed getter alignment fixtures, and compile checks across kernel header versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/nlattr.h -->
