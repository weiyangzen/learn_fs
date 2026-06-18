# sources/distributed-fs/ceph-client/net/mac80211/tests/util.h

## Purpose
This header declares the shared mac80211 KUnit fixture API implemented by `tests/util.c`. It gives test files a compact way to allocate a fake `ieee80211_sub_if_data` environment as a KUnit-managed resource.

## Important APIs, types, and functions
- `struct t_sdata` is the fixture wrapper. It contains pointers to fake `ieee80211_sub_if_data` and `wiphy`, an embedded `ieee80211_local`, optional `ctx`, and embedded 2 GHz/5 GHz supported-band structs.
- `T_SDATA(test)` allocates the fixture using `kunit_alloc_resource(test, t_sdata_init, t_sdata_exit, GFP_KERNEL, NULL)`, asserts success, and returns the wrapper.
- `t_sdata_init()` and `t_sdata_exit()` are declared for the KUnit resource lifecycle.

## Control flow
Consumers include this header, call `T_SDATA(test)` inside a KUnit test, and receive a fully initialized wrapper or fail the test through `KUNIT_ASSERT_NOT_NULL()`. KUnit owns the resource and invokes `t_sdata_exit()` during cleanup.

## State and persistence
The header defines the shape of per-test state but no global state. The returned wrapper persists for the lifetime of the KUnit resource. The embedded `ieee80211_local` is stable by address and is referenced by the fake `sdata->local` pointer.

## Dependencies and integration points
The header includes `../ieee80211_i.h`, which exposes internal mac80211 structures unavailable through the public API. It is intended only for in-tree mac80211 tests. The macro wraps KUnit resource management and therefore assumes the caller runs in a KUnit test context.

## Risks and edge cases
Because the macro contains an assertion and returns an expression, it is convenient but not suitable for non-KUnit or setup paths that need ordinary error propagation. The fixture intentionally exposes internal mutable structures; tests can modify them freely, so cross-test isolation depends on each test allocating its own resource. The header currently names only 2 GHz and 5 GHz bands in `struct t_sdata`, matching the implementation.

## Test signals
The header itself has no standalone tests. Its signal comes from dependent KUnit suites: successful use demonstrates that the fixture ABI and implementation still agree with current mac80211 internal structure layouts.
