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
