# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_test.h

## Purpose

`xe_test.h` provides conditional test-only declarations and helpers for Xe KUnit builds, including a small base private-data type used to identify test-specific `kunit->priv` payloads.

## Important APIs, Types, and Definitions

- `enum xe_test_priv_id` with `XE_TEST_LIVE_DMA_BUF` and `XE_TEST_LIVE_MIGRATE`.
- `struct xe_test_priv` containing the ID.
- Test-build macros: `XE_TEST_DECLARE(x)` and `XE_TEST_ONLY(x)`.
- `xe_cur_kunit_priv(enum xe_test_priv_id id)` returns the current KUnit private base if present and matching.
- Non-test builds compile these helpers away.

## Control Flow

In KUnit-enabled builds, `xe_cur_kunit_priv` checks for a current KUnit test, reads `test->priv`, compares the embedded ID, and returns it or NULL. In non-KUnit builds the helper always returns NULL and test-only declarations disappear.

## State and Persistence Behavior

The header does not own state. It interprets `current->kunit->priv` when a running test supplies a structure embedding `struct xe_test_priv`.

## Dependencies and Integration Points

It depends conditionally on KUnit headers and is used by production code that needs minor test-only behavior without affecting non-test builds, plus live tests that tag private data.

## Risks and Edge Cases

- `xe_cur_kunit_priv` assumes `test->priv` is non-NULL and points to an object whose first member is `struct xe_test_priv`; misuse can dereference invalid memory.
- Test-only hooks must remain compiled out of production builds.
- Adding new test private IDs requires keeping producer and consumer code synchronized.

## Test Signals

Build coverage under both KUnit and non-KUnit configs is the main signal. Runtime signals are correct test-private dispatch in dma-buf/migrate test paths without affecting production behavior.
