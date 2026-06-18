# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_test.c

## Purpose

`scoped_test.c` is a minimal validation test for the `.scoped` field of `struct landlock_ruleset_attr`. It checks that unknown high-order scope bits are rejected rather than silently accepted.

## Important APIs, Types, and Functions

The test uses `landlock_create_ruleset()` directly with `.scoped = scoped_mask`, kselftest `TEST()`/`ASSERT_EQ`, and `LANDLOCK_SCOPE_SIGNAL` as the highest known scope bit boundary.

## Control Flow and State

The loop starts at bit 63 and shifts down until it reaches `LANDLOCK_SCOPE_SIGNAL`, expecting every unknown bit to make `landlock_create_ruleset()` fail with `EINVAL`. It creates no persistent Landlock domain because all calls are expected to fail.

## Dependencies and Integration Points

It depends on the local Landlock UAPI header defining known scope bits and on the kernel rejecting unknown scope masks.

## Risks and Test Signals

The main risk is ABI laxness: accepting unknown bits would make future scope semantics ambiguous. The signal is strict `-1` plus `errno == EINVAL` for every unknown mask.
