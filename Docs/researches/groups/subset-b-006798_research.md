# subset-b-006798 Research

This grouped report covers Linux BPF selftest host-side harnesses under `sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests`. Each section is source-tree-aligned and intended to be split into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_distill.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_distill.c

## Purpose
This file validates libbpf BTF base distillation and split-BTF relocation behavior. It fabricates base and split BTF graphs, distills only referenced base types into a compact base BTF, and verifies that relocation back against a full base BTF succeeds or fails for the right ambiguity and missing-type cases.

## APIs, Types, and Functions
The test uses libbpf BTF construction APIs such as `btf__new_empty`, `btf__new_empty_split`, `btf__add_int`, `btf__add_struct`, `btf__add_field`, `btf__add_union`, `btf__add_enum`, `btf__add_enum64`, `btf__add_func_proto`, `btf__add_array`, `btf__distill_base`, and `btf__relocate`. `VALIDATE_RAW_BTF` from `btf_helpers.h` is the main structural oracle. The important local routines are `test_distilled_base`, the duplicate-name and error variants, `test_distilled_base_vmlinux`, and `test_distilled_endianness`.

## Control Flow
Each subtest builds one or more BTF objects, validates their raw type layout, calls `btf__distill_base`, validates the distilled split/base pair, and optionally calls `btf__relocate` against a candidate base. The primary path checks named composites are represented as empty references while anonymous composites, function prototypes, and arrays needed by split BTF are copied into split BTF. Error subtests intentionally create indistinguishable or missing base types and expect `-EINVAL`.

## State, Dependencies, and Integration
State is in-memory `struct btf` objects only; cleanup frees every BTF handle. The vmlinux test depends on loadable kernel BTF and the host's `int` type. Endianness coverage deliberately serializes and reparses raw BTF with the inverse endianness.

## Risks and Test Signals
The signal is exact raw BTF text and expected success/error returns. Regressions are likely if libbpf changes type-id remapping, anonymous type copy rules, duplicate-name disambiguation, or BTF endianness propagation. The file is environment-sensitive only for vmlinux BTF availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_distill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_dump.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_dump.c

## Purpose
This file exercises `btf_dump` C type emission and typed data formatting. It compares generated C declarations from BTF-bearing object files against embedded expected output, then validates value dumping for kernel BTF types, synthetic floats, strings, DATASEC variables, and edge cases such as overflow, zero elision, type tags, and anonymous naming conflicts.

## APIs, Types, and Functions
Core APIs include `btf__parse_elf`, `btf__parse`, `libbpf_find_kernel_btf`, `btf_dump__new`, `btf_dump__dump_type`, `btf_dump__dump_type_data`, `btf__find_by_name`, `btf__resolve_size`, and BTF builder APIs for incremental cases. `struct btf_dump_test_case` enumerates fixture objects; `struct test_ctx` owns an in-memory BTF plus `open_memstream` dump buffer. Helper callbacks are `btf_dump_printf` and `btf_dump_snprintf`.

## Control Flow
`test_btf_dump_case` parses each `.bpf.o`, forces pointer size where necessary, writes all dumped declarations to a temp file, and compares with an `awk | diff` extraction from the corresponding source fixture. `test_btf_dump_incremental` checks that already-emitted names influence later conflict resolution. `test_btf_dump_type_tags` checks C attributes for type tags and attrs. The value dump path constructs a dump object over kernel BTF, then subtests integers, floats, chars, typedefs, enums, structs/unions, variables, strings, and DATASEC output using macros that compare exact string output and return sizes.

## State, Dependencies, and Integration
Persistent state is limited to temporary files under `/tmp`, deleted after diffing. The test depends on fixture BPF objects and sources, kernel BTF, libc `open_memstream`, host compiler support for optional `__int128`, and libbpf's BTF dump implementation. It integrates with selftest subtest dispatch through `test__start_subtest`.

## Risks and Test Signals
Exact string comparisons make this a high-sensitivity formatting regression test. Risks include fragile dependency on kernel BTF type names and layouts, architecture pointer-size assumptions, shell `awk`/`diff` behavior, and generated output changes that are semantically valid but textually different.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_endian.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_endian.c

## Purpose
This test verifies that libbpf can serialize, parse, and modify BTF in both native and opposite byte order. It specifically checks BTF header byte swapping, type-count preservation, and correct interpretation of a newly added variable after endianness transitions.

## APIs, Types, and Functions
The file uses `btf__parse_elf`, `btf__endianness`, `btf__set_endianness`, `btf__raw_data`, `btf__new`, `btf__add_var`, `btf__type_by_id`, `btf__str_by_offset`, and `btf_var`. It inspects `struct btf_header` and `struct btf_type`, using `bswap_16` to confirm serialized magic bytes.

## Control Flow
`test_btf_endian` loads fixture BTF from `btf_dump_test_case_syntax.bpf.o`, flips the BTF object's endianness, obtains raw data, reparses it as a new BTF, compares raw bytes, and checks that the swapped header encodes `BTF_MAGIC` when byte-swapped. It then flips the reloaded object back to native endianness, validates the native header, appends a variable to the original BTF, serializes in swapped order again, and ensures the reloaded type is readable with the expected name, linkage, and referred type.

## State, Dependencies, and Integration
All state is in-memory BTF raw buffers owned by libbpf BTF objects. It depends on compile-time `__BYTE_ORDER__`, the BTF fixture object, and libbpf's raw-data cache invalidation after mutation.

## Risks and Test Signals
The main signal is successful cross-endian parsing plus header and type metadata equality. Failures indicate byte-order regressions, stale raw-data caching after BTF mutation, or fixture availability problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_endian.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_field_iter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_field_iter.c

## Purpose
This file validates libbpf internal BTF field iteration over all supported BTF kind layouts. It fabricates representative BTF types and checks that each raw type exposes the expected type-id and string fields through `btf_field_iter`.

## APIs, Types, and Functions
The `fields` table holds expected `ids` and `strs` for each type. The test builds BTF with `btf__add_int`, pointer, array, struct, union, enum, fwd, typedef, qualifiers, function prototype/function, vars, float, decl/type tags, enum64, and datasec APIs. It uses `btf_field_iter` and `btf_field_iter_next` from `bpf/libbpf_internal.h`.

## Control Flow
`test_btf_field_iter` creates a synthetic BTF, validates its raw dump, then iterates type IDs from 1 to `btf__type_cnt() - 1`. For each type it initializes the field iterator and walks every exposed field, comparing discovered type IDs and strings against the corresponding expected row in `fields`.

## State, Dependencies, and Integration
State is a single in-memory `struct btf`. This is an internal libbpf behavior test rather than a kernel verifier test; it depends on exact struct layout knowledge embedded in libbpf's BTF field iterator.

## Risks and Test Signals
The test detects omissions or ordering changes in internal BTF metadata traversal. Because expectations are aligned to fabricated type IDs, any builder behavior change that changes ID assignment, vlen, or field traversal ordering can fail the test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_field_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_kind.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_kind.c

## Purpose
This test covers BTF kind layout metadata used to decode future or unrecognized BTF kinds. It checks that raw BTF can optionally include a layout table and that a BTF with an otherwise unknown kind can be decoded when the layout section describes its shape.

## APIs, Types, and Functions
It uses `btf__new_empty_opts` with `LIBBPF_OPTS(btf_new_opts, .add_layout = true)`, `btf__raw_data`, `btf__add_int`, `btf__add_typedef`, `btf__parse`, `btf__find_by_name`, `btf__type_by_id`, and low-level mutation of `struct btf_header`, `struct btf_layout`, and `struct btf_type`. `write_raw_btf` persists synthetic raw BTF into temp files for parser tests.

## Control Flow
`test_btf_kind_encoding` creates empty BTF with and without layout metadata and asserts header offsets and lengths. `test_btf_kind_decoding` builds normal BTF, copies its raw bytes, appends or modifies layout metadata, overwrites one typedef's kind to `BTF_KIND_MAX + 1`, and verifies parse failure or success depending on the presence and correctness of kind layout entries. `test_btf_kind` dispatches encoding and decoding subtests.

## State, Dependencies, and Integration
The file uses temporary `/tmp/test_btf_kind.*` files and raw memory buffers. It depends on libbpf's experimental or recent BTF layout support and on the kernel/libbpf UAPI definitions for `struct btf_layout`.

## Risks and Test Signals
Strong signals are header layout assertions, parser success/failure, and ability to find later named types after the unknown kind. Risks are high around UAPI version skew, raw buffer mutation, and layout alignment assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_kind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_map_in_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_map_in_map.c

## Purpose
This file validates BTF-declared map-in-map definitions, including array-of-maps, hash-of-maps, dynamic inner maps, and rejection of incompatible inner map sizes for sockmap-like nesting.

## APIs, Types, and Functions
It uses the generated `test_btf_map_in_map.skel.h` skeleton, `bpf_map__fd`, `bpf_map_get_info_by_fd`, `bpf_map_update_elem`, `bpf_map_lookup_elem`, and skeleton open/load/attach/destroy helpers. `bpf_map_id` reads map IDs for identity checks.

## Control Flow
`test_lookup_update` opens and attaches the skeleton, retrieves inner and outer map FDs, updates outer maps to point at different inner maps, changes `skel->bss->input`, sleeps briefly to let the attached program run, and checks values written into the selected inner maps. It then repeatedly swaps inner map FDs and verifies map IDs are obtainable. `test_diff_size` attempts to insert an incompatible inner sock array into an outer map and expects failure. `test_btf_map_in_map` runs both subtests.

## State, Dependencies, and Integration
State lives in kernel BPF maps and skeleton BSS during the test and is destroyed with the skeleton. Integration is through BPF object metadata generated from the companion program and libbpf's map-in-map creation logic.

## Risks and Test Signals
The important signals are correct map update routing, expected inner-map values, successful map info lookup, and rejection of size-mismatched inner maps. Races are minimized with `usleep`, but scheduling or attach failures can still make this environment-sensitive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_map_in_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_module.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_module.c

## Purpose
This small test verifies loading BTF for the selftest kernel module `bpf_testmod` and finding a known exported symbol in that module BTF.

## APIs, Types, and Functions
It uses `btf__load_vmlinux_btf`, `btf__load_module_btf`, `btf__find_by_name`, `btf__free`, and the global selftest environment flag `env.has_testmod`.

## Control Flow
`test_btf_module` skips when the test module is unavailable. Otherwise it loads vmlinux BTF, loads module BTF with vmlinux as the base, searches for `bpf_testmod_test_read`, asserts a positive type ID, and frees both BTF objects.

## State, Dependencies, and Integration
No persistent state is created. The test depends on the selftest module being loaded or discoverable, sysfs kernel/module BTF support, and valid vmlinux base BTF.

## Risks and Test Signals
The only success signal is a positive symbol type ID. Failures point to missing test module setup, module BTF load regressions, or symbol name drift in `bpf_testmod`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_permute.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_permute.c

## Purpose
This file tests `btf__permute`, which reorders BTF type IDs and rewrites all internal type references. It covers both standalone base BTF and split BTF that references a base BTF.

## APIs, Types, and Functions
The test uses BTF builders, `btf__permute`, `VALIDATE_RAW_BTF`, `btf__new_empty_split`, and arrays of target IDs. `permute_base_check` and `permute_split_check` validate canonical postconditions. `test_permute_base` and `test_permute_split` exercise success and failure cases.

## Control Flow
The base test constructs a small graph of `int`, pointer, typedef, struct, const, and volatile types, validates it, applies a permutation, and checks that IDs and type references changed consistently. It then attempts invalid permutations such as duplicate targets, invalid IDs, wrong array length, and inclusion of ID zero, confirming the BTF remains unchanged after errors. The split test repeats the pattern where split-local IDs are permuted while base IDs remain stable.

## State, Dependencies, and Integration
State is entirely in-memory `struct btf` objects. The file integrates with libbpf's BTF mutation logic and with `btf_helpers.h` raw dump assertions.

## Risks and Test Signals
The core signal is exact raw BTF after permutation and unchanged BTF after invalid calls. Regressions are likely in reference rewriting, split/base ID boundary handling, and validation of permutation arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_permute.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_sanitize.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_sanitize.c

## Purpose
This file validates libbpf's BTF sanitization when a kernel feature is missing. It specifically checks that BTF layout metadata is removed when `FEAT_BTF_LAYOUT` is marked unsupported.

## APIs, Types, and Functions
It defines a synthetic `struct layout_btf` containing a `struct btf_header`, one encoded int type, layout entries, and strings. It uses `btf__new`, `btf__raw_data`, `bpf_object_set_feat_cache`, `kernel_supports`, `bpf_object__sanitize_btf`, and the `kfree_skb` skeleton object as a host `bpf_object`.

## Control Flow
`test_btf_sanitize_layout` opens the skeleton, parses the synthetic BTF, confirms nonzero `layout_off` and `layout_len`, allocates a feature cache that marks all features supported except `FEAT_BTF_LAYOUT`, installs it on the object, and asserts the feature gates. Sanitization should return BTF with layout offsets zeroed, strings moved after types, unchanged string length, and a smaller raw size.

## State, Dependencies, and Integration
State includes a manually allocated feature cache transferred to the skeleton object and BTF objects freed at exit. This test integrates with libbpf's internal feature-detection cache and BTF object sanitization path.

## Risks and Test Signals
The signal is header-level structural change, not verifier execution. Risks include UAPI layout changes, ownership of the feature cache, and mismatches between skeleton object feature probing and manual feature cache overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_sanitize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_skc_cls_ingress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_skc_cls_ingress.c

## Purpose
This network integration test validates BTF-enabled access to socket/kernel TCP state from a TC ingress classifier, including regular connection paths and SYN cookie generation/receipt paths for IPv4, IPv6, and dual-stack listeners.

## APIs, Types, and Functions
It uses `test_btf_skc_cls_ingress.skel.h`, libbpf TC APIs (`bpf_tc_hook_create`, `bpf_tc_attach`), netns helpers, socket helpers (`start_server`, `connect_to_fd`, `v6only_true`, `v6only_false`), and sysctl writes for TCP options. Key helpers are `prepare_netns`, `reset_test`, `print_err_line`, `run_test`, and small wrappers for six subcases.

## Control Flow
The test opens and loads the skeleton, creates a dedicated network namespace, attaches the classifier to loopback ingress, enables TCP options required for syncookie helper behavior, and then iterates through connection and syncookie subtests. `run_test` sets syncookie mode, starts a server with the requested address family, copies server addresses into BPF BSS, connects a client, accepts it, and validates BSS observations: listen socket port, request socket port, generated/received cookie equality, and MSS bounds.

## State, Dependencies, and Integration
State spans a temporary network namespace, TC qdisc/filter on loopback, sysctls inside the namespace, sockets, and skeleton BSS. Cleanup is via netns destruction and skeleton destruction. It depends on CAP_NET_ADMIN-like privileges, syncookie support, IPv6, loopback, and BTF field compatibility with the BPF program.

## Risks and Test Signals
Signals are BSS counters and socket observations. Risks include namespace/sysctl setup failures, kernel TCP behavior changes, missing helper support, and asynchronous network behavior that can obscure BPF-side field access errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_skc_cls_ingress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_split.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_split.c

## Purpose
This file tests split and multi-split BTF creation, serialization, parsing, and C declaration dumping. It verifies that split BTF inherits base metadata, keeps split-local types out of the base, and can round-trip raw BTF files without corrupting type IDs.

## APIs, Types, and Functions
It uses `btf__new_empty`, `btf__new_empty_split`, BTF builder APIs, `btf__set_pointer_size`, `btf__find_str`, `btf__type_by_id`, `btf__raw_data`, `btf__parse`, `btf__parse_split`, `btf_dump__new`, and `btf_dump__dump_type`. `btf_raw_write` writes raw BTF to temp files; `__test_btf_split` implements both single and multi-split cases.

## Control Flow
The test creates a base BTF with `int`, pointer, and `struct s1`, then a split BTF with `struct s2` referencing base types. In multi mode it creates a third BTF layer with `union u1` referencing split types. It validates type visibility, dumps all types to an in-memory stream, compares expected declarations, writes raw base/split/multisplit BTF to temp files, reparses them with proper bases, and byte-compares parsed type records against originals.

## State, Dependencies, and Integration
State includes in-memory BTF objects, dump buffers, and temp files under `/tmp`. It depends on libbpf split-BTF parser semantics and `btf_dump` output. Pointer size is forced to 8 to avoid host architecture drift.

## Risks and Test Signals
Signals include inherited pointer size, type visibility, exact dump text, raw write byte counts, parse success, type-count equality, and per-type memory equality. Risks are temp-file cleanup, strict text matching, and split-base ID boundary regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_split.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_sysfs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_sysfs.c

## Purpose
This file validates mmap behavior for BTF blobs exposed through sysfs, currently `/sys/kernel/btf/vmlinux`. It ensures the mapping is read-only/private, rejects invalid protections and sizes, zero-fills page padding, and remains parseable as BTF.

## APIs, Types, and Functions
It uses `stat`, `open`, `mmap`, `mprotect`, `munmap`, `sysconf`, and `btf__new_split`. The helper `test_btf_mmap_sysfs` accepts a BTF sysfs path and optional base BTF.

## Control Flow
The helper determines BTF size and page-rounded end, rejects writable private mapping, shared read mapping, and overlarge mapping, then accepts a page-rounded private read mapping. It verifies that changing protections to write or exec fails, scans padding bytes beyond `st_size` up to the rounded end for zeros, and parses the mapped bytes as BTF.

## State, Dependencies, and Integration
State is a file descriptor and memory mapping, both cleaned up locally. The test depends on kernel sysfs BTF support, mmap semantics for the BTF binary attribute, and enough permissions to read `/sys/kernel/btf/vmlinux`.

## Risks and Test Signals
The test is a kernel ABI signal for BTF sysfs mmap restrictions. Risks include architecture page-size differences, sysfs file absence, mapping length mistakes, and changes in allowed mmap flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_tag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_tag.c

## Purpose
This file tests BTF declaration tags and type tags in BPF programs, including module, vmlinux, `__user`, and per-CPU pointer cases. It ensures skeletons load when compiler/kernel support exists and skips cleanly when tag attributes are missing.

## APIs, Types, and Functions
It uses skeletons `test_btf_decl_tag`, `btf_type_tag`, `btf_type_tag_user`, and `btf_type_tag_percpu`, plus BTF APIs `btf__load_vmlinux_btf`, `btf__load_module_btf`, `btf__find_by_name_kind`, and `btf__free`. `load_btfs` centralizes vmlinux/module BTF loading and feature skips. The file defines a host `struct btf_type_tag_test` referenced by generated skeleton metadata.

## Control Flow
Basic subtests open/load skeletons and inspect `rodata->skip_tests`. The module/user paths call `load_btfs`, optionally set BTF custom paths on skeleton open options, load BPF objects, and validate whether program loading succeeds based on whether the referenced tagged type should be resolvable. Per-CPU variants follow the same pattern for per-CPU tag use. `test_btf_tag` dispatches all subtests.

## State, Dependencies, and Integration
State is limited to skeleton objects and loaded BTF handles. The test depends on `bpf_testmod`, vmlinux BTF, module BTF, compiler support for BTF tag attributes, and kernel support for tagged pointer validation.

## Risks and Test Signals
Signals are skeleton load success/failure and explicit skips. Risks include kernel/module BTF lacking `user` type tags, test module absence, and compiler-generated BTF differences that change `skip_tests` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_tag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_write.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_write.c

## Purpose
This file validates libbpf's writable BTF builder APIs, raw dump output, BTF appending, split-BTF appending, and deduplication after combining split BTFs. It is a broad unit test for constructing every important BTF kind programmatically.

## APIs, Types, and Functions
`gen_btf` exercises `btf__add_str`, `btf__add_int`, pointer and qualifiers, arrays, struct/union fields, enum/enum64 values, typedef, fwd, float, func/proto/params, var, datasec, decl tag, and type tag APIs, then inspects `struct btf_type`, members, params, vars, and raw dumps. `test_btf_add`, `test_btf_add_btf`, and `test_btf_add_btf_split` cover creation, copying one BTF into another via `btf__add_btf`, split-BTF copying, and `btf__dedup`.

## Control Flow
The base add subtest creates empty BTF and calls `gen_btf`, which validates both successful additions and invalid inputs. The add-BTF subtest builds two independent BTFs, copies one into another, and validates ID offsets and raw layout. The split test creates a base, two split BTFs referencing the base and their own local types, appends both into a combined split BTF, validates type counts before and after dedup, and confirms duplicate typedefs collapse while references remain coherent.

## State, Dependencies, and Integration
All state is in-memory BTF. It depends on `btf_helpers.h` formatting and current libbpf semantics for ID allocation, raw type layout, and deduplication.

## Risks and Test Signals
Exact ID and raw dump assertions provide strong regression signals for builder behavior. Risks include brittleness to intentional BTF formatting changes and subtle split-ID remapping bugs when copying or deduplicating split BTFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/build_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/build_id.c

## Purpose
This serial test validates build-ID collection from BPF stack traces for uprobes, contrasting no-fault and sleepable helpers when the target executable's build ID is resident or paged out.

## APIs, Types, and Functions
It uses `test_build_id.skel.h`, `read_build_id`, `bpf_program__attach`, `system("./uprobe_multi ...")`, and `struct bpf_stack_build_id`. `print_stack` formats stack frames for verbose output. `subtest_nofault` and `subtest_sleepable` attach different BPF programs and inspect skeleton BSS stack buffers.

## Control Flow
`serial_test_build_id` reads the expected build ID from the `uprobe_multi` binary, then runs three subtests. The no-fault path attaches a uprobe, triggers either paged-in or paged-out executable behavior, checks the BPF result length, and expects either `BPF_STACK_BUILD_ID_VALID` with matching bytes or `BPF_STACK_BUILD_ID_IP` when the build ID is not resident. The sleepable path triggers paged-out behavior but expects valid build ID collection.

## State, Dependencies, and Integration
State is skeleton BSS plus the target process image state influenced by `uprobe_multi`. The test depends on the `uprobe_multi` helper binary, build IDs in ELF notes, uprobe attach support, and stack build-ID helper behavior.

## Risks and Test Signals
Signals are stack frame status and build-ID byte equality. Risks include missing helper binary, build IDs stripped from test binaries, paging behavior differences, and uprobe attach permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/build_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cb_refs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cb_refs.c

## Purpose
This verifier-negative test validates reference tracking across callback-style BPF programs. It ensures selected programs fail to load with specific verifier diagnostics for invalid callback reference transfer, leaks, underflow, or nested-callback reference ownership.

## APIs, Types, and Functions
It uses `cb_refs.skel.h`, `bpf_object_open_opts` with a large kernel verifier log buffer, `bpf_object__find_program_by_name`, `bpf_program__set_autoload`, skeleton load/destroy helpers, and `bpf_prog_test_run_opts` with `pkt_v4` input from network helpers.

## Control Flow
For each entry in `cb_refs_tests`, the test opens the skeleton with verifier logging, autoloads only the named program, expects skeleton load to fail, optionally runs the program if load unexpectedly succeeds, and checks that the verifier log contains the expected diagnostic substring.

## State, Dependencies, and Integration
State is the global verifier log buffer and transient skeleton object. It integrates directly with kernel verifier diagnostics, so it depends on exact or near-exact verifier wording.

## Risks and Test Signals
The test signal is expected load failure plus diagnostic substring match. It is intentionally brittle to verifier message changes but valuable for catching reference-tracking regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cb_refs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cg_storage_multi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cg_storage_multi.c

## Purpose
This serial cgroup test validates cgroup local storage semantics when multiple programs and attach types are involved. It distinguishes egress-only, isolated per-attach-type storage, and shared cgroup storage behavior across parent and child cgroups.

## APIs, Types, and Functions
It uses cgroup and network helpers, `struct cgroup_value` from `progs/cg_storage_multi.h`, skeletons `cg_storage_multi_egress_only`, `cg_storage_multi_isolated`, and `cg_storage_multi_shared`, `bpf_program__attach_cgroup`, and map lookup helpers. Local helpers `assert_storage`, `assert_storage_noexist`, and `connect_send` drive assertions and traffic.

## Control Flow
The serial entry creates parent and child cgroups, then runs three subtests. `test_egress_only` attaches parent then child egress programs and checks packet counters keyed by cgroup ID and attach type. `test_isolated` attaches two egress and one ingress program at parent and child, verifying separate ingress and egress storage keys. `test_shared` repeats the topology but expects combined ingress/egress counters under a shared cgroup ID key.

## State, Dependencies, and Integration
State spans cgroup hierarchy, UDP sockets, kernel BPF maps, links, and skeleton BSS invocation counters. Cgroups and links are closed/destroyed after each path. It depends on cgroup v2 helpers, networking, and local storage map semantics.

## Risks and Test Signals
Signals are exact invocation counts and map values after traffic. Risks include cgroup setup failures, socket traffic not triggering expected hooks, or key schema changes between isolated and shared storage maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cg_storage_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup1_hierarchy.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup1_hierarchy.c

## Purpose
This test validates BPF cgroup ancestor checks for cgroup v1 hierarchies, using LSM programs triggered by fentry attachment. It covers correct ancestor ID/hierarchy ID, root cgroup ID behavior, sleepable LSM behavior, and invalid ID handling.

## APIs, Types, and Functions
It uses `test_cgroup1_hierarchy.skel.h`, `setup_cgroup_environment`, `setup_classid_environment`, `join_classid`, `get_classid_cgroup_id`, `get_cgroup1_hierarchy_id`, `bpf_program__set_attach_target`, `bpf_program__attach_lsm`, and `bpf_program__attach_trace`. Helpers are `bpf_cgroup1`, `bpf_cgroup1_sleepable`, and `bpf_cgroup1_invalid_id`.

## Control Flow
The test opens the skeleton, sets `target_pid`, retargets fentry to `bpf_fentry_test1`, loads, sets up cgroup v1 net_cls hierarchy, joins it, records current cgroup and hierarchy IDs in BSS, and runs subtests. Normal and root cases expect the LSM program to block the fentry attach. The invalid-ID case expects fentry attach success because the ancestor condition should not match.

## State, Dependencies, and Integration
State includes cgroup v1/classid setup, current process membership, skeleton BSS fields, and transient LSM/fentry links. Cleanup tears down cgroup environments. It depends on cgroup v1 net_cls availability and BPF LSM/fentry support.

## Risks and Test Signals
Signals are attach success or failure in the expected direction and link destroy success. Environment risk is high on systems without cgroup v1 net_cls or required BPF attach capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup1_hierarchy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_ancestor.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_ancestor.c

## Purpose
This TC/network cgroup test validates BPF helper logic for resolving ancestor cgroup IDs at multiple levels from packet context.

## APIs, Types, and Functions
It uses `cgroup_ancestor.skel.h`, cgroup helpers, network namespace helpers, TC hook APIs (`bpf_tc_hook_create`, `bpf_tc_attach`, detach/destroy), IPv6 UDP sockets, and `get_cgroup_id`. `struct test_data` owns the skeleton, TC hook/options, and namespace token.

## Control Flow
The test loads the skeleton, joins/creates `/skb_cgroup_test`, builds a netns with loopback and TC egress filter attached to the BPF program, sends an IPv6 datagram to `::1`, and then compares the BSS `cgroup_ids` array with expected root, current, test cgroup, and zero-for-missing levels.

## State, Dependencies, and Integration
State spans a named network namespace, TC qdisc/filter on loopback, cgroup membership, and skeleton BSS. Cleanup detaches TC, destroys qdisc, closes namespace, deletes netns, and closes cgroup FD.

## Risks and Test Signals
The signal is exact ancestor ID matching after packet traversal. Risks include netns command failures, loopback/TC setup issues, cgroup ID interpretation changes, and packet not traversing the attached egress hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_ancestor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_attach_autodetach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_attach_autodetach.c

## Purpose
This serial test verifies automatic detachment and eventual program release when a cgroup with attached programs is removed without explicit detach.

## APIs, Types, and Functions
It hand-builds a minimal `BPF_PROG_TYPE_CGROUP_SKB` allow program using raw BPF instructions and `bpf_test_load_program`. It uses `setup_cgroup_environment`, `create_and_get_cgroup`, `join_cgroup`, `bpf_prog_attach`, `bpf_prog_query`, `bpf_prog_get_fd_by_id`, and shell `ping`.

## Control Flow
The test loads two allow programs, creates and joins `/cg_autodetach`, attaches both with `BPF_F_ALLOW_MULTI`, queries their IDs, sends loopback traffic, allocates memory to keep the cgroup pinned, closes program and cgroup FDs, leaves/removes the cgroup via cleanup, then polls up to roughly five seconds for `bpf_prog_get_fd_by_id` to fail for each old program ID.

## State, Dependencies, and Integration
State includes cgroup hierarchy, attached BPF programs, program IDs, loopback traffic, and a temporary heap allocation. Cleanup closes any remaining program/cgroup FDs and resets cgroup environment.

## Risks and Test Signals
The signal is disappearance of program IDs after asynchronous auto-detach. Risks are timing sensitivity, ping availability, cgroup cleanup behavior, and delayed RCU/program release on busy kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_attach_autodetach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_attach_multi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_attach_multi.c

## Purpose
This serial test validates legacy multi/override cgroup program attach semantics, effective program ordering through cgroup hierarchy, replacement behavior, detach behavior, and query edge cases.

## APIs, Types, and Functions
It uses raw BPF instruction construction in `prog_load_cnt`, creating an array map plus cgroup storage and percpu cgroup storage maps. It calls `bpf_test_load_program`, `bpf_prog_attach`, `bpf_prog_attach_opts`, `bpf_prog_detach2`, `bpf_prog_query`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, and cgroup helper functions. `PING_CMD` triggers egress hooks.

## Control Flow
The test loads several programs that add distinct values to a shared map, sets up nested cgroups, attaches programs with combinations of `BPF_F_ALLOW_MULTI`, `BPF_F_ALLOW_OVERRIDE`, and no flags, sends traffic, and verifies the accumulated value corresponds to the effective program set. It checks duplicate attach rejection, effective query counts and ENOSPC behavior, bottom-program detach, replace failure modes, valid replace including self-replace, and subsequent detach effects.

## State, Dependencies, and Integration
State includes nested cgroups, multiple loaded program FDs, shared array map, local storage maps, and loopback traffic. Cleanup closes programs, map FD, cgroup FDs, and cgroup environment.

## Risks and Test Signals
Signals are map counter sums, query counts, attach flags, program IDs, and expected errno values. The test is sensitive to cgroup hook ordering, legacy attach semantics, ping availability, and exact errno behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_attach_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_attach_override.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_attach_override.c

## Purpose
This serial test validates `BPF_F_ALLOW_OVERRIDE` behavior for cgroup skb programs. It checks that child cgroup programs can override parent decisions and that effective program execution changes as programs are attached/detached through a hierarchy.

## APIs, Types, and Functions
It hand-loads small cgroup skb programs with `prog_load(int verdict)`, using raw BPF instructions that return allow or deny. The test uses cgroup helpers, `bpf_prog_attach`, `bpf_prog_detach2`, `bpf_prog_query`, and loopback `ping` as traffic.

## Control Flow
The test sets up a nested cgroup hierarchy, attaches allow and deny programs with override flags at different levels, joins the deepest cgroup, runs pings, and observes whether traffic succeeds according to the closest overriding program. It also queries effective program counts/IDs and detaches programs to validate fallback to parent behavior.

## State, Dependencies, and Integration
State is cgroup hierarchy and loaded program FDs. It integrates with legacy cgroup attach APIs rather than skeletons. Cleanup closes all FDs and resets the cgroup environment.

## Risks and Test Signals
The main signal is ping success/failure plus effective query results. Risks include timing/availability of `ping`, cgroup hierarchy setup, and kernel changes to override semantics or query ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_attach_override.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_dev.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_dev.c

## Purpose
This test validates cgroup device controller BPF program behavior for allowing and denying `mknod`, read, and write operations on device nodes.

## APIs, Types, and Functions
It uses `dev_cgroup.skel.h`, cgroup helpers, `mknod`, `open`, `read`, `write`, `makedev`, `bpf_program__attach_cgroup`, and skeleton BSS/rodata state. Helper routines `test_mknod`, `test_read`, and `test_write` assert return values and errno.

## Control Flow
The test joins a cgroup, loads the device cgroup skeleton, attaches `bpf_prog1`, and runs subtests that set skeleton-side access expectations before performing device operations. It checks allowed mknod/read/write and denied operations, including wrong-device-type behavior.

## State, Dependencies, and Integration
State includes a test cgroup, attached device BPF program, temporary device node paths, and skeleton variables used by the BPF program. It requires privileges for cgroup device hooks and `mknod`.

## Risks and Test Signals
Signals are syscall return values and errno matches. Risks include filesystem/device permission restrictions, missing cgroup device BPF support, and cleanup of created device nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_get_current_cgroup_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_get_current_cgroup_id.c

## Purpose
This file validates `bpf_get_current_cgroup_id` from a cgroup-attached program by comparing the BPF-observed ID with the user-space cgroup ID.

## APIs, Types, and Functions
It uses `get_cgroup_id_kern.skel.h`, `cgroup_setup_and_join`, `get_cgroup_id`, `bpf_program__attach_cgroup`, and a device operation trigger through `mknod`/`makedev` headers included for the underlying test path.

## Control Flow
The test creates and joins a test cgroup, loads the skeleton, attaches its cgroup program, triggers the hook, and asserts that the ID written by the BPF program matches `get_cgroup_id` for the current cgroup.

## State, Dependencies, and Integration
State is the cgroup membership and skeleton BSS result. Cleanup destroys the skeleton and cgroup environment. It depends on cgroup setup helpers and cgroup ID visibility.

## Risks and Test Signals
The signal is exact cgroup ID equality. Risks are mostly environmental: inability to create/join the cgroup, missing attach support, or a trigger path that does not execute the program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_get_current_cgroup_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_getset_retval.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_getset_retval.c

## Purpose
This test validates cgroup getsockopt/setsockopt hooks that read and set syscall return values. It checks retval propagation, override ordering, legacy reject compatibility, synchronization between context retval and helper-visible retval, and which hook sections are exposed.

## APIs, Types, and Functions
It uses skeletons `cgroup_getset_retval_setsockopt`, `cgroup_getset_retval_getsockopt`, and `cgroup_getset_retval_hooks`, plus `bpf_program__attach_cgroup`, `setsockopt`, `getsockopt`, `start_server`, and `bpf_object__find_program_by_name`. The generated `exposed_hooks` table comes from `cgroup_getset_retval_hooks.h`.

## Control Flow
The entry joins a cgroup and starts a UDP server socket. Setsockopt subtests attach combinations of programs that set errno, read retval, default to zero, or perform legacy EPERM-style rejection; then they call `setsockopt` and assert errno, invocation count, assertion flags, and BSS retval. Getsockopt subtests perform analogous checks for kernel errors, BPF override, and clearing retval. `test_exposed_hooks` iterates hook names, enables one at a time, and checks load return against expected errors.

## State, Dependencies, and Integration
State is cgroup membership, socket FD, BPF links, and skeleton BSS counters. Each subtest destroys links and skeletons. The test integrates with cgroup socket option hooks and newer retval helper semantics.

## Risks and Test Signals
Signals are syscall return/errno, BSS `invocations`, `assertion_error`, `retval_value`, and `ctx_retval_value`. Risks include kernel version support for retval hooks, exact errno semantics, and generated hook table drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_getset_retval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_hierarchical_stats.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_hierarchical_stats.c

## Purpose
This integration test validates hierarchical aggregation of cgroup attach counters using BPF iterators pinned in bpffs. It creates a cgroup tree, attaches processes to leaf cgroups, dumps counters through cgroup iter links, and checks parent totals.

## APIs, Types, and Functions
It uses bpffs mount helpers (`mount`, `umount`, path removal), cgroup helpers, `fork`/`waitpid`, `bpf_program__attach_iter`, `bpf_link__pin`, file reads, and `cgroup_hierarchical_stats.skel.h`. Important helpers include `setup_bpffs`, `setup_cgroups`, `attach_processes`, `setup_cgroup_iter`, `setup_progs`, and `check_attach_counters`.

## Control Flow
The test prepares bpffs and a fixed cgroup hierarchy, opens/loads the skeleton, creates one cgroup iterator link per cgroup plus root with `BPF_CGROUP_ITER_SELF_ONLY`, pins links under bpffs, attaches the BPF programs, forks child processes to join leaf cgroups, reads generated files, parses `cg_id` and `attach_counter`, and validates leaf counts and parent sums.

## State, Dependencies, and Integration
State includes mounted bpffs, pinned BPF iterator links, cgroup hierarchy, child process joins, generated bpffs files, and skeleton links. Cleanup removes pinned files, destroys skeletons, closes cgroup FDs, and unmounts bpffs when mounted by the test.

## Risks and Test Signals
Signals are parsed file format, nonzero counters, exact leaf count of three, parent-child sum equality, and root lower-bound checks. Risks are bpffs mount permissions, cgroup process accounting timing, fork failures, and stale pinned files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_hierarchical_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_iter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_iter.c

## Purpose
This file tests cgroup BPF iterator traversal modes and parameter validation. It verifies preorder, postorder, ancestor-up, self-only, children-only, early termination, invalid cgroup specs, dead cgroup handling, and CSS task iteration.

## APIs, Types, and Functions
It uses `cgroup_iter.skel.h`, `iters_css_task.skel.h`, `bpf_program__attach_iter`, `bpf_iter_create`, `read`, `union bpf_iter_link_info`, cgroup helpers, and `kern_sync_rcu`. Static arrays track cgroup paths, FDs, IDs, and expected output text.

## Control Flow
Setup creates root, parent, and child cgroups and records IDs. `read_from_cgroup_iter` attaches an iterator with requested order, reads output, and compares with `expected_output`. Subtests cover invalid fd/id combinations, traversal orders, terminal-cgroup early termination, self-only output, children output, and reading an iterator after its target cgroup has been removed. The CSS task subtest loads a separate skeleton and verifies the current PID's CSS task count.

## State, Dependencies, and Integration
State includes cgroup hierarchy, iterator links and FDs, skeleton BSS controls such as `terminal_cgroup` and `terminate_early`, and expected string buffers. Cleanup destroys skeletons and cgroup environment.

## Risks and Test Signals
Signals are exact iterator output strings, expected attach errors, and CSS task count. Risks include RCU timing for dead cgroups, formatting changes in iterator programs, and environment support for cgroup iterators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_iter_memcg.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_iter_memcg.c

## Purpose
This test validates memory-cgroup iterator statistics by creating anonymous, file-backed, shared-memory, and page-fault activity and checking BPF-reported memcg counters.

## APIs, Types, and Functions
It uses `cgroup_iter_memcg.skel.h`, `cgroup_iter_memcg.h`, cgroup helpers, `bpf_program__attach_iter`, `bpf_iter_create`, `read`, `mmap`, file I/O, and the `struct memcg_query` shared with the BPF program. Helpers include `read_stats`, `test_anon`, `test_file`, `test_shmem`, and `test_pgfault`.

## Control Flow
The test joins a cgroup, loads the skeleton, attaches a memcg iterator link, and runs subtests that allocate/touch memory in different ways. After each activity, `read_stats` drains the iterator FD so the BPF program updates shared query fields, and assertions compare counters for anonymous memory, file cache, shmem, and page faults.

## State, Dependencies, and Integration
State includes cgroup membership, memory mappings, temporary file-backed pages, iterator link/FD, and BPF BSS query data. It depends on memcg accounting, mmap behavior, page cache updates, and cgroup iterator support.

## Risks and Test Signals
Signals are counter increases in expected categories. Risks include memory accounting races, kernel configuration differences for memcg, lazy page faulting, and noisy background memory activity in the test cgroup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_iter_memcg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_link.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_link.c

## Purpose
This serial test validates link-based cgroup program attachment, effective program queries, link update, mixing with legacy attaches, and detach behavior in nested cgroup hierarchies.

## APIs, Types, and Functions
It uses `test_cgroup_link.skel.h`, `bpf_program__attach_cgroup`, `bpf_link__destroy`, `bpf_link_update`, `bpf_link_get_info_by_fd`, `bpf_prog_query`, `bpf_prog_attach`, `bpf_prog_detach2`, and cgroup helpers. `ping_and_check` resets skeleton counters, runs `ping`, and checks primary/alternate program invocation counts.

## Control Flow
The test creates four nested cgroups, joins the deepest, attaches one link at each level, and verifies traffic sees all effective programs. It queries local and effective attach state, destroys the bottom link, mixes in a legacy multi attach, reattaches a link, exercises link update to an alternate program, validates link info, and cleans up both link and legacy attachments.

## State, Dependencies, and Integration
State includes nested cgroup FDs, BPF links, optional legacy attachment, skeleton BSS counters, and loopback traffic. Cleanup destroys live links, detaches legacy program when used, closes cgroups, and resets cgroup environment.

## Risks and Test Signals
Signals are invocation counters, query counts/IDs, link info fields, and update results. Risks include ping availability, effective cgroup ordering changes, and interactions between link-based and legacy attach APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_mprog_opts.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_mprog_opts.c

## Purpose
This file tests the newer cgroup multi-program attach, detach, query, and link APIs with explicit ordering options and revision checks. It covers normal, preorder, link-based, and invalid option combinations.

## APIs, Types, and Functions
It uses `cgroup_mprog.skel.h`, `bpf_prog_attach_opts`, `bpf_prog_detach_opts`, `bpf_prog_query_opts`, `bpf_link_create`, `bpf_link_update`, `bpf_link_detach`, `id_from_prog_fd`, and cgroup helpers. `assert_mprog_count` wraps `bpf_prog_query` count assertions.

## Control Flow
`test_prog_attach_detach` attaches four programs with `BPF_F_BEFORE`, `BPF_F_AFTER`, `relative_fd`, and `expected_revision`, queries IDs/revision/order, then detaches with revision validation. `test_link_attach_detach` performs analogous operations through BPF links and checks link IDs. Preorder variants verify `BPF_F_PREORDER` combinations. `test_invalid_attach_detach` exercises bad relative FDs, bad revisions, conflicting flags, missing multi/preorder requirements, and invalid detach options. The entry runs these across supported attach types.

## State, Dependencies, and Integration
State is a test cgroup, loaded skeleton programs, program/link IDs, and kernel mprog revision counters. Cleanup paths carefully detach in reverse order and destroy skeletons.

## Risks and Test Signals
Signals are exact program/link ordering, revision values, counts, and expected errno for invalid cases. This is sensitive to kernel mprog API evolution and attach-type support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_mprog_opts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_mprog_ordering.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_mprog_ordering.c

## Purpose
This test validates multi-program ordering for cgroup getsockopt hooks when `BPF_F_BEFORE` is used with and without an explicit relative FD.

## APIs, Types, and Functions
It reuses `cgroup_preorder.skel.h`, cgroup helpers, `bpf_prog_attach_opts`, `bpf_prog_detach2`, `bpf_program__expected_attach_type`, and a TCP socket `getsockopt` trigger. `run_getsockopt_test` implements one ordering check.

## Control Flow
The entry joins `/parent`, creates a socket, and invokes `run_getsockopt_test` twice. Each run attaches `parent`, then attaches `parent_2` with `BPF_F_ALLOW_MULTI | BPF_F_BEFORE`, optionally setting `relative_fd` to the first program. A `getsockopt(IP_TOS)` call triggers both programs, and the skeleton BSS `result` array must record the expected order `4, 3`.

## State, Dependencies, and Integration
State is one cgroup FD, socket FD, skeleton BSS result array, and temporary program attachments. Cleanup detaches both programs and destroys the skeleton.

## Risks and Test Signals
The signal is BSS ordering after getsockopt. Risks include unsupported mprog ordering flags, attach-type mismatch, and socket option behavior differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_mprog_ordering.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_preorder.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_preorder.c

## Purpose
This file validates `BPF_F_PREORDER` execution ordering for cgroup getsockopt programs across parent and child cgroups and within the same cgroup.

## APIs, Types, and Functions
It uses `cgroup_preorder.skel.h`, `bpf_prog_attach_opts`, `bpf_prog_detach2`, `bpf_program__expected_attach_type`, cgroup helpers, and `setsockopt`/`getsockopt` on `IP_TOS`. `run_getsockopt_test` performs the attach and trigger sequence.

## Control Flow
The test creates parent and child cgroups, opens a socket, and runs the helper twice: once with mixed default/preorder flags and once with all attachments preorder. The helper attaches two child programs, triggers getsockopt and checks child-only order, resets BSS, attaches two parent programs, triggers again, and validates the full parent/child execution order for the selected mode.

## State, Dependencies, and Integration
State includes cgroup FDs, socket TOS value, skeleton BSS `idx` and `result`, and four temporary program attachments. Cleanup detaches every program and closes resources.

## Risks and Test Signals
The signal is exact BSS result ordering. Risks include kernel preorder semantics changes, attach-type support, and getsockopt not traversing the expected cgroup hook path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_preorder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_skb_direct_packet_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_skb_direct_packet_access.c

## Purpose
This compact test verifies that a cgroup skb program can be run through `BPF_PROG_TEST_RUN` and directly access packet data boundaries.

## APIs, Types, and Functions
It uses `cgroup_skb_direct_packet_access.skel.h`, `bpf_prog_test_run_opts`, `bpf_program__fd`, and a 64-byte zeroed test skb buffer.

## Control Flow
The test opens and loads the skeleton, runs the `direct_packet_access` program with packet data via test-run opts, asserts the syscall succeeds, expects retval `1`, and checks that the BPF program wrote a nonzero `data_end` value into BSS.

## State, Dependencies, and Integration
State is limited to the input buffer and skeleton BSS. It does not attach to a real cgroup; it integrates with the kernel test-run path for cgroup skb programs.

## Risks and Test Signals
Signals are test-run success, return value, and BSS `data_end`. Risks include verifier/test-run changes for direct packet access and program type restrictions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_skb_direct_packet_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_skb_sk_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_skb_sk_lookup.c

## Purpose
This test validates `sk_lookup` behavior from a cgroup skb ingress program, ensuring clients in the attached cgroup can be steered to a listening socket while a socket created outside the cgroup does not connect normally.

## APIs, Types, and Functions
It uses `cgroup_skb_sk_lookup_kern.skel.h`, `bpf_program__attach_cgroup`, `test__join_cgroup`, and network helpers such as `start_server`, `connect_fd_to_fd`, `connect_to_fd`, and `accept`.

## Control Flow
The entry creates an IPv6 TCP socket before joining the test cgroup so it retains the outside cgroup association. `run_cgroup_bpf_test` loads the skeleton, joins `/foo`, attaches the ingress lookup program, and calls `run_lookup_test`. That helper starts a server, stores its port in BPF BSS, verifies the outside socket times out with `EINPROGRESS`, then verifies an inside-cgroup client connects and is accepted.

## State, Dependencies, and Integration
State includes sockets, cgroup membership, attached link, and skeleton BSS server port. Cleanup closes all sockets/Fds and destroys the skeleton.

## Risks and Test Signals
Signals are outside connection failure and inside connection success. Risks include IPv6 availability, TCP timing, socket cgroup association semantics, and sk_lookup helper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_skb_sk_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_storage.c

## Purpose
This file tests classic cgroup local storage behavior for packet filtering and an out-of-bounds verifier/runtime guard path.

## APIs, Types, and Functions
It uses `cgroup_storage.skel.h`, cgroup helpers, network namespace helpers, `bpf_program__attach_cgroup`, map get-next-key/lookup/update APIs, and shell `ping`. `setup_network` creates a dedicated namespace with loopback up; `cleanup_network` removes it.

## Control Flow
`test_cgroup_storage` creates and joins a cgroup, enters a netns, loads and attaches the BPF program, and sends pings that should alternate success/failure based on a packet counter stored in cgroup storage. It reads the storage key/value, increments the counter from user space, verifies the alternating behavior continues, and asserts there is only one storage key. `test_cgroup_storage_oob` loads the same skeleton, attaches a program intended to trigger an out-of-bounds local-storage access path, and drives it through a socket operation.

## State, Dependencies, and Integration
State includes cgroup membership, netns, BPF link, cgroup storage map entries, and shell ping traffic. Cleanup destroys the skeleton, namespace, cgroup FD, and cgroup environment.

## Risks and Test Signals
Signals are ping success/failure sequence, map lookup/update correctness, single-key enumeration, and expected handling of OOB access. Risks include ping/netns setup failures, packet timing, and local storage map semantics changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_storage.c -->
