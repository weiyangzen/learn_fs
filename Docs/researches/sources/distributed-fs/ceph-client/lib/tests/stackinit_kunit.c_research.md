## sources/distributed-fs/ceph-client/lib/tests/stackinit_kunit.c

### Purpose
This KUnit suite validates compiler-based stack variable initialization, especially `-ftrivial-auto-var-init={zero,pattern}` and STRUCTLEAK-style clearing. It detects whether scalars, arrays, structs, unions, padding holes, user-pointer structs, copy assignments, and switch-scope declarations leak prior stack contents.

### Important APIs, types, and functions
The file uses macro generation to create many `do_nothing_*`, `leaf_*`, and `test_*` functions. Global tracking (`check_buf`, `fill_start`, `target_start`, `fill_size`, `target_size`) records the tested stack slot and copied bytes. `DEFINE_TEST()` creates a leaf function that optionally fills a local variable with `FILL_BYTE`, then later exposes the compiler-initialized bytes through `memcpy(check_buf, ...)`. `DEFINE_TEST_DRIVER()` performs the two-call fill/extract protocol, validates stack-frame overlap with `stackinit_range_contains()`, and fails or skips expected-failure cases based on `xfail`.

### Control flow
Macro families generate tests for scalar zero/none, char arrays, structs with small/big/trailing padding holes, packed structs, user-pointer structs, and unions with same or mismatched member sizes. Initialization modes include zero, old zero, static/dynamic/runtime partial/all, assigned static/dynamic partial/all, assigned copy, and none. Special switch tests cover variables declared before the first `case`, which compilers often cannot initialize. The suite registers a large flat KUnit case table grouped by expected behavior.

### State and persistence
Global tracking buffers are overwritten by each test. There is no heap allocation and no persistent kernel object. The “state” under test is transient stack content, with `forced_mask` volatile to keep the compiler from optimizing away fills.

### Dependencies and integration points
The suite depends on KUnit, compiler instrumentation options, kernel config symbols such as `CONFIG_INIT_STACK_NONE`, architecture-specific `CONFIG_M68K`, and `__user` annotations. It integrates as suite `stackinit`.

### Risks and edge cases
Expectations are intentionally compiler- and configuration-dependent. Some tests use XFAIL/skip semantics when uninitialized bytes are expected, so skip counts can represent known gaps rather than infrastructure failures. Stack-frame colocation is checked because compiler layout differences could otherwise invalidate the fill/extract comparison. Copy-assignment tests are expected to fail because copying preserves padding bytes.

### Test signals
Signals include detection of any retained `FILL_BYTE`, assertion that fill and target stack ranges overlap, KUnit skips for expected uninitialized bytes, and broad generated coverage over scalar, array, struct, union, padding, user field, and switch declaration cases.
