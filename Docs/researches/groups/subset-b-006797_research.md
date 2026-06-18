# Research: subset-b-006797

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf.c

## Purpose

`btf.c` is a large BPF selftest suite for kernel and libbpf BTF behavior. It hand-builds raw BTF byte streams, loads them through `bpf_btf_load()`, attaches them to maps and programs, reads BTF and program metadata back through kernel info APIs, validates BPF map pretty-print output from bpffs, and verifies libbpf BTF deduplication results. The file is test-only code, but it exercises kernel ABI contracts around `struct btf_header`, BTF kind validation, map BTF key/value typing, `BPF_PROG_LOAD` func/line info, `BPF_OBJ_GET_INFO_BY_FD`, and libbpf's in-memory `btf__dedup()` implementation.

## Important APIs, Types, And Data

The test harness depends on kernel UAPI and libbpf APIs from `<linux/bpf.h>`, `<linux/btf.h>`, `<bpf/bpf.h>`, and `<bpf/btf.h>`, plus selftest helpers from `test_progs.h`, `bpf_util.h`, and `../test_btf.h`. It uses raw BTF construction macros such as `BTF_TYPE_INT_ENC`, `BTF_TYPE_ENC`, `BTF_ARRAY_ENC`, `BTF_MEMBER_ENC`, `BTF_FUNC_PROTO_ENC`, `BTF_LINE_INFO_ENC`, `BTF_VAR_ENC`, `BTF_DECL_TAG_ENC`, `BTF_TYPE_TAG_ENC`, and `BTF_END_RAW` to encode test cases as arrays of `__u32`.

`struct btf_raw_test` drives the raw BTF verifier and map-creation tests. Its fields describe the raw type records, string section, optional map parameters, expected BTF load failure, expected map creation failure, header offset perturbations, pretty-print map traits, and map value layout kind. `raw_tests[]` is the central matrix of verifier cases. It covers valid and invalid structs/unions/enums/arrays, global data `VAR`/`DATASEC`, header layout gaps and overlaps, loops, invalid names, function prototypes and functions, kind flags, bitfields, 128-bit integers, data section names, floats, `DECL_TAG`, `TYPE_TAG`, and `ENUM64`.

`struct btf_get_info_test` and `get_info_tests[]` cover BTF info retrieval. Special callbacks `test_big_btf_info()` and `test_btf_id()` validate larger-than-known `bpf_btf_info` structs, BTF object IDs, `bpf_btf_get_fd_by_id()`, and the propagation of BTF IDs/type IDs into `struct bpf_map_info`.

`struct btf_file_test` and `file_tests[]` test BTF embedded in object files. The suite parses `test_btf_newkv.bpf.o` and `test_btf_nokv.bpf.o`, loads programs with libbpf, checks legacy map BTF key/value metadata, and reads function info from the loaded program's kernel BTF.

The pretty-print lane defines `struct pprint_mapv`, optional `struct pprint_mapv_int128`, `pprint_test_template[]`, and `pprint_tests_meta[]`. These encode map value layouts with scalars, holes, bitfields, anonymous unions, enums, arrays, per-CPU layout, and optional `__int128`, then compare the text exported by reading a pinned bpffs map.

`struct prog_info_raw_test` and `info_raw_tests[]` drive program-level func/line-info tests. They combine raw BTF, BPF instruction arrays, `func_info`, `line_info`, expected load failures, and dead-code/dead-function masks. Helper routines validate the kernel's adjusted function metadata, source line info, JIT line info, JIT symbols, and function lengths.

`struct btf_dedup_test`, `struct btf_raw_data`, and `dedup_tests[]` drive libbpf-only deduplication tests. They compare input BTF after `btf__dedup()` against an expected BTF graph for string compaction, duplicate type folding, forward declaration resolution, tags, recursive typedefs, data sections, enum/enum64 semantics, and name conflict cases.

## Control Flow

`test_btf()` is the exported selftest entry point. It sets `always_log` from `env.verbosity`, then iterates `raw_tests`, `get_info_tests`, `file_tests`, `info_raw_tests`, `dedup_tests`, and finally runs `test_pprint()`. Each iteration is wrapped by `test__start_subtest()`, so individual failures are reported as named subtests rather than as one monolithic test.

Raw BTF testing flows through `do_test_raw()`. It calls `btf_raw_create()` to synthesize a complete BTF blob from a header template, raw type records, and a string section. It optionally mutates header fields with per-test deltas, loads the blob through `load_raw_btf()`, checks the expected load result and optional verifier log substring, and, if requested, creates a BPF map with `bpf_map_create()` and BTF key/value IDs. `load_raw_btf()` retries failed loads with a verifier log buffer when logging was not already enabled.

`btf_raw_create()` is a key internal constructor. It computes the type-section byte length with `get_raw_sec_size()`, builds an index of strings from the provided string section, replaces `NAME_TBD` and `NAME_NTH(n)` placeholders with actual string offsets, fills header `type_len`, `str_off`, and `str_len`, and returns an allocated raw BTF blob. This lets compact test fixtures express type names in declaration order while still exercising exact BTF wire encoding.

`do_test_get_info()` loads a raw BTF blob, asks the kernel to copy BTF bytes back into a user buffer with `bpf_btf_get_info_by_fd()`, and validates returned ID, info length, reported BTF size, copied bytes, and untouched bytes when the supplied buffer is shorter than the real BTF size. `test_big_btf_info()` verifies ABI extension handling for trailing bytes in `struct bpf_btf_info`. `test_btf_id()` verifies object ID lookup and BTF lifetime through maps.

`do_test_file()` parses BTF and optional BTF.ext from object files, temporarily relaxes libbpf strict map definition rules, opens and loads a BPF object, checks map BTF key/value IDs, then reads `struct bpf_func_info` records from `bpf_prog_get_info_by_fd()`. When BTF.ext exists, it loads the program BTF back by kernel ID and matches the function names `_dummy_tracepoint`, `test_long_fname_1`, and `test_long_fname_2`.

`test_pprint()` populates the first pretty-print template with each map type from `pprint_tests_meta[]`, then runs the remaining templates against an array map. `do_test_pprint()` loads BTF, creates a map, pins it under `/sys/fs/bpf/<map_name>`, writes deterministic values for all keys and CPUs, reads the pinned map as text, skips comment lines, and compares every output line with `get_pprint_expected_line()`. Per-CPU maps expect a nested key block with one line per CPU; unordered maps derive the expected key from the line itself; lossy LRU maps do not require every entry to be present.

Program metadata testing flows through `do_test_info_raw()`. It builds BTF, patches `NAME_TBD` placeholders in line info with `patch_name_tbd()`, fills a `union bpf_attr`, and calls the `bpf()` syscall with `BPF_PROG_LOAD`. Successful program loads are checked by `test_get_finfo()` and `test_get_linfo()`. These helpers account for dead code and dead function pruning by checking expected counts and masks, and they validate monotonic instruction offsets, source metadata preservation, and JIT line-info placement when JIT output is available.

Dedup testing flows through `do_test_dedup()`. It creates libbpf `struct btf` objects from input and expected raw BTF data, sets `struct btf_dedup_opts.sz`, runs `btf__dedup()`, obtains raw data from both objects, compares total size and string section length, verifies all expected strings are present with identical content, compares type counts, and checks each type's encoded size, kind, info, and size/type field. The comparison deliberately focuses on canonicalized raw representation and string availability, not on pointer identity.

## State And Persistence Behavior

The file has no long-lived repository state or production persistence. Runtime state is confined to static globals `duration`, `always_log`, and `btf_log_buf`, plus stack/heap allocations and kernel object file descriptors. Kernel state is created transiently through BTF FDs, map FDs, and program FDs, and is released by `close()` in each test's cleanup path. Pretty-print tests temporarily pin maps in bpffs under `/sys/fs/bpf/<map_name>` and remove them with `unlink(pin_path)` before exit. Object-file tests open libbpf objects and BTF objects and free/close them on cleanup.

The most visible external side effects are verifier log text on stderr, pinned bpffs map paths during `do_test_pprint()`, and temporarily loaded kernel BTF/map/program objects while tests are running. `libbpf_set_strict_mode()` is temporarily relaxed in `do_test_file()` for legacy map definitions, then restored to `LIBBPF_STRICT_ALL` in the `done` block.

## Dependencies And Integration Points

This file integrates with the Linux selftests BPF framework. It expects a kernel with BTF and BPF syscall support, libbpf APIs, bpffs mounted at `/sys/fs/bpf`, and selftest object files such as `test_btf_newkv.bpf.o` and `test_btf_nokv.bpf.o` in the test working directory. It also depends on selftest-generated BTF encoding macros from `test_btf.h` and assertion/subtest macros from `test_progs.h`.

Kernel integration points include `bpf_btf_load()`, `bpf_btf_get_info_by_fd()`, `bpf_btf_get_fd_by_id()`, `bpf_map_create()`, `bpf_map_get_info_by_fd()`, `bpf_map_update_elem()`, `bpf_obj_pin()`, `bpf_prog_get_info_by_fd()`, and direct `syscall(__NR_bpf, BPF_PROG_LOAD, ...)`. Libbpf integration points include `btf__new()`, `btf__raw_data()`, `btf__type_cnt()`, `btf__type_by_id()`, `btf__find_str()`, `btf__str_by_offset()`, `btf__parse_elf()`, `btf_ext__free()`, `btf__load_from_kernel_by_id()`, `bpf_object__open()`, `bpf_object__load()`, `bpf_object__next_program()`, `bpf_object__find_map_by_name()`, `bpf_program__set_type()`, `bpf_program__fd()`, `bpf_map__btf_key_type_id()`, `bpf_map__btf_value_type_id()`, and `btf__dedup()`.

## Risks And Edge Cases

The test is intentionally coupled to exact kernel verifier messages for many negative cases through `err_str` substring checks. Kernel changes that preserve behavior but alter log wording can break the test. It is also sensitive to BTF binary encoding, BTF kind semantics, type ID renumbering after dedup, map BTF validation rules, and program loader behavior around dead-code pruning.

Several tests require privileged BPF operations, bpffs, JIT-dependent metadata, and architecture-specific sizes. The code uses `sizeof(void *)`, optional `__SIZEOF_INT128__`, per-CPU map value rounding, and JIT presence checks, so portability depends on test harness support and kernel configuration. Pretty-print tests assume the textual map renderer's field ordering and formatting remain stable. Object-file tests depend on test fixture availability and compiler/linker ordering of functions, with explicit accommodation only for the second and third expected function names.

Memory and resource cleanup is mostly handled with `goto done` paths, but early returns can skip later test steps. `do_test_pprint()` unlinks `pin_path` in cleanup even when the path was not populated by a successful `snprintf()`, although the local buffer is zero-initialized only by stack state if not assigned; in practice cleanup is reached after the path is written or after allocation/load failures. Program info validation also has a suspicious assignment in the JIT-line loop, `cur_func_len = jited_ksyms[ksyms_found]`, where the surrounding logic suggests it may have intended `jited_func_lens[ksyms_found]`; because this is test code, the practical risk is false failure or missed bounds validation on some JIT layouts.

The raw fixture arrays are dense and manually maintained. Adding or editing one BTF record often requires coordinated changes to string ordering, `NAME_TBD` consumption, expected type IDs, map value sizes, and expected error substrings. The helper `get_raw_sec_size()` scans backward for `BTF_END_RAW`; missing sentinels will be caught as a negative size but can make fixture issues non-obvious.

## Test Signals

Positive signals include named subtests passing across all raw verifier cases, successful map creation where expected, expected verifier log substrings for negative BTF loads, successful `bpf_btf_get_info_by_fd()` byte-for-byte comparisons, correct BTF IDs in map info, matching loaded function names from object-file BTF, exact pretty-print line comparisons for array/hash/per-CPU/LRU map types, successful program loads and expected metadata counts, and exact dedup canonicalization against expected BTF.

Failure signals are mostly `CHECK()` assertions with contextual stderr, including mismatched expected load failures, missing `err_str`, invalid map FDs, unexpected EOF or extra bpffs pretty-print output, wrong function/line info counts, non-monotonic line offsets, bad JIT symbol/function accounting, dedup size/type/string mismatches, or inability to load/parsing fixtures. The dispatcher's exhaustive loops mean a regression in any matrix entry is isolated to the subtest name from the corresponding `descr` field.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_dedup_split.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_dedup_split.c

## Purpose

`btf_dedup_split.c` is a focused libbpf selftest for BTF deduplication when a split BTF object is layered on top of a base BTF object. It creates synthetic base and split BTF graphs with `btf__new_empty()` and `btf__new_empty_split()`, validates their raw layouts, runs `btf__dedup()`, and verifies that duplicates, forward declarations, anonymous structs, and module split-BTF references are resolved as expected. The file complements the broader `btf.c` dedup tests by exercising split-BTF ID spaces and base/split type reference behavior.

## Important APIs, Types, And Data

The test uses libbpf BTF construction APIs from `<bpf/btf.h>` and test helpers from `test_progs.h` and `btf_helpers.h`. Important APIs include `btf__new_empty()`, `btf__new_empty_split()`, `btf__set_pointer_size()`, `btf__pointer_size()`, `btf__add_int()`, `btf__add_ptr()`, `btf__add_struct()`, `btf__add_field()`, `btf__add_fwd()`, `btf__find_str()`, `btf__type_by_id()`, `btf__str_by_offset()`, `btf__dedup()`, `btf__parse_split()`, `btf__load_vmlinux_btf()`, `btf__type_cnt()`, `btf__find_by_name_kind()`, `btf_params()`, `btf_vlen()`, and type predicates such as `btf_is_int()`, `btf_is_func_proto()`, `btf_is_mod()`, `btf_is_ptr()`, and `btf_is_typedef()`.

The file relies on assertion and raw dump helpers: `ASSERT_OK_PTR`, `ASSERT_OK`, `ASSERT_EQ`, `ASSERT_NEQ`, `ASSERT_GE`, `ASSERT_GT`, `ASSERT_LT`, `ASSERT_STREQ`, and `VALIDATE_RAW_BTF`. The `mod_funcs[]` array lists module functions that should have split-BTF function prototypes whose core kernel type parameters ultimately resolve to base vmlinux BTF: `bpf_testmod_test_write`, `bpf_kfunc_call_test3`, and `bpf_kfunc_call_test_pass_ctx`.

`btf_add_dup_struct_in_cu()` is a local fixture builder that adds an `int`, a named struct `s`, and two duplicate anonymous structs to a supplied BTF object. Its `start_id` argument lets the same relative graph be added either to a standalone/base BTF or to a split BTF whose local additions begin after base type IDs.

## Control Flow

`test_btf_dedup_split()` is the exported entry point. It runs five subtests through `test__start_subtest()`: `split_simple`, `split_struct_duped`, `split_fwd_resolve`, `split_dup_struct_in_cu`, and `split_module`.

`test_split_simple()` builds a base BTF with `int`, `int *`, and `struct s1 { int f1; }`, then creates an empty split BTF on top. It verifies that pointer size is inherited from the base and that base strings/types are visible through the split object. The split object then adds `struct s2` referencing both duplicated split types and base types, plus duplicate `int` and duplicate `struct s1`. Before dedup, the C dump has a renamed duplicate `struct s1___2`; after `btf__dedup()`, the duplicate int and duplicate struct are folded into the base IDs and `struct s2` references the canonical base `struct s1`, `int`, and pointer types.

`test_split_fwd_resolve()` builds a base BTF with recursive `struct s1`, concrete `struct s2`, and unrelated concrete `struct s3`. The split BTF adds duplicate `int`, a duplicate recursive `struct s1`, a forward declaration of `s2`, and a forward declaration of `s3`. After dedup, the split `struct s1` and `int` are removed as duplicates, the split forward declaration of `s2` is resolved to base `struct s2`, and an unresolved pointer to `s3` remains only as needed. This tests split dedup's ability to resolve forward declarations against base BTF while preserving references that are not part of the deduplicated graph.

`test_split_struct_duped()` starts with a base BTF containing `int`, a forward declaration of `s2`, and `struct s1` that points to itself and to the forward `s2`. The split BTF adds duplicate `int`, duplicate `struct s1`, a concrete `struct s2`, a pointer to the split forward `s2`, and `struct s3` containing that pointer. After dedup, the split duplicate `int` is folded into the base `int`, but the split concrete `s1`/`s2` graph is preserved as new split types because it extends the forward declaration context. The test validates exact post-dedup type IDs for the remaining pointer, concrete structs, and `struct s3`.

`test_split_dup_struct_in_cu()` first uses `btf_add_dup_struct_in_cu()` to generate duplicate anonymous structs in a standalone base object, dedups it so both fields of `struct s` point to one canonical anonymous struct, then creates split BTF and adds the same duplicate graph again. A second `btf__dedup()` should reduce the split additions entirely back to the already deduplicated base graph. The final raw BTF for the split object should match the original deduped base data.

`test_split_module()` is the only test that reads system BTF. It loads vmlinux BTF, remembers the base type count, parses `/sys/kernel/btf/bpf_testmod` as split BTF over vmlinux, and verifies selected module functions. For each function it finds the `BTF_KIND_FUNC`, follows its `type` to the `FUNC_PROTO`, iterates parameters, strips reference wrappers (`mod`, `ptr`, `typedef`) until reaching a concrete type, and asserts that the final concrete type ID is less than `nr_base_types`. This ensures module split BTF refers back to base kernel types instead of carrying duplicated core kernel types in the split object.

## State And Persistence Behavior

The file has no persistent application state. All synthetic `struct btf *` objects are heap-backed libbpf objects freed with `btf__free()` on cleanup paths. Pointer size is set explicitly on base or fixture BTF objects to make dumps stable on 64-bit assumptions, and split BTF inherits pointer size from its base object. The module test temporarily opens vmlinux and module BTF data from `/sys/kernel/btf`, but it does not write to the filesystem or create kernel objects.

Raw validation state is expressed entirely through `VALIDATE_RAW_BTF()` expected strings. Type IDs are intentionally part of the state being tested: split BTF exposes base type IDs first and appends split-local IDs after the base count, so dedup changes are validated through exact ID rewrites.

## Dependencies And Integration Points

The test integrates with libbpf's in-memory BTF construction, split-BTF, C dump, and dedup logic. It also integrates with the BPF selftest framework for subtest selection and assertions. `test_split_module()` depends on a running kernel that exposes `/sys/kernel/btf/vmlinux` through `btf__load_vmlinux_btf()` and has the `bpf_testmod` module BTF available at `/sys/kernel/btf/bpf_testmod`. It also assumes the module exports BTF for the named functions in `mod_funcs[]`.

The important behavioral contract is that `btf__new_empty_split(base)` produces a split BTF view where base strings and types are addressable, local additions begin after base type IDs, and `btf__dedup()` can deduplicate local types against both local and base BTF without corrupting base IDs. The module integration further depends on resilient split-BTF generation from the kernel build tooling, but the test avoids asserting whether wrapper reference types themselves are base or split because that depends on pahole support.

## Risks And Edge Cases

The tests are highly sensitive to exact libbpf raw BTF dump formatting and type ID assignment. A valid libbpf implementation change that canonicalizes types in a different order, renames duplicate C dump types differently, or changes raw dump text could require fixture updates. The synthetic graphs intentionally include recursive pointers, duplicate concrete structs, forward declarations, anonymous duplicate structs, and split/base references, so off-by-one type IDs or wrong base-vs-split ID handling are the main regression risks.

`test_split_module()` can skip or fail depending on host kernel configuration. Missing vmlinux BTF, missing `bpf_testmod`, module not loaded, or differences in generated module BTF can prevent the test from running to completion. There is also an early-return path after `btf__parse_split()` failure that does not free `vmlinux_btf`; this is test process cleanup rather than persistent leakage, but it is still a local resource cleanup weakness.

The module test intentionally follows `mod`, `ptr`, and `typedef` chains until a non-wrapper type. If future BTF kinds become common wrappers for module parameters, the test could falsely fail by checking the wrapper ID rather than its concrete base target. Conversely, because it only verifies final concrete type IDs are from base BTF, it does not validate the full function prototype shape beyond existence, kind, and parameter target provenance.

## Test Signals

The synthetic tests signal success through exact `VALIDATE_RAW_BTF()` layouts before and after dedup, exact `btf_type_c_dump()` strings in `split_simple`, pointer-size inheritance checks, string lookup through split BTF, and successful `btf__dedup()` returns. Failures identify the subtest name and assertion label, such as `empty_main_btf`, `empty_split_btf`, `btf_dedup`, `inherit_ptr_sz`, `int_kind`, or `c_dump`.

The module test signals success when vmlinux BTF loads, module split BTF parses, each named function is found as a split function ID, the function's type is a function prototype, and every parameter resolves through wrappers to a base BTF type ID. Failures in this lane point to missing module BTF, missing functions, malformed prototype links, or core kernel types being duplicated into split BTF instead of referenced from the base.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_dedup_split.c -->
