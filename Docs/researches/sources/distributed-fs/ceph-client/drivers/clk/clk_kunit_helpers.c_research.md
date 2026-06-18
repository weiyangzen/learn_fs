# sources/distributed-fs/ceph-client/drivers/clk/clk_kunit_helpers.c

## Purpose

`clk_kunit_helpers.c` provides test-managed wrappers for common clock framework operations. It converts manual cleanup requirements such as `clk_put()`, `clk_disable_unprepare()`, `clk_hw_unregister()`, and `of_clk_del_provider()` into KUnit actions that run automatically when a test exits or immediately on setup failure.

## Important APIs, Types, And Functions

`clk_prepare_enable_kunit()` calls `clk_prepare_enable()` and registers a reset action that calls `clk_disable_unprepare()`. `clk_get_kunit()`, `of_clk_get_kunit()`, and `clk_hw_get_clk_kunit()` wrap their respective get functions and funnel successful results through `__clk_get_kunit()`, which registers a `clk_put()` action. `clk_hw_get_clk_prepared_enabled_kunit()` composes managed `clk_hw_get_clk()` with managed prepare/enable.

Provider helpers include `clk_hw_register_kunit()` and `of_clk_hw_register_kunit()`, which register a hardware clock and attach automatic `clk_hw_unregister()`. `of_clk_add_hw_provider_kunit()` registers an OF hardware provider and attaches automatic `of_clk_del_provider()`. Action wrappers are declared with `KUNIT_DEFINE_ACTION_WRAPPER`.

## Control Flow

Each helper follows the same pattern: perform the real clock operation, return the original error if it fails, then call `kunit_add_action_or_reset()`. If the cleanup action cannot be added, KUnit immediately runs the reset action, so partially initialized resources do not leak into later tests. Composition is explicit in `clk_hw_get_clk_prepared_enabled_kunit()`: get the consumer first, then prepare/enable it, returning an error pointer if either stage fails.

## State And Persistence Behavior

The helpers do not own persistent state. They register cleanup callbacks in the KUnit resource/action system. Clock state changes are delegated to the common clock core, and test lifetime determines cleanup ordering. Returned clocks remain valid until the test action runs or the caller manually drops them only if it deliberately bypasses the managed lifetime contract.

## Dependencies And Integration Points

The file depends on public clock consumer/provider APIs, KUnit resources, error-pointer conventions, and OF provider APIs. It is compiled as a GPL module helper for tests and exported with `EXPORT_SYMBOL_GPL()` so KUnit test objects can use the wrappers. `clk_test.c` uses these helpers for provider registration, OF provider registration, managed consumer gets, and managed prepare/enable.

## Risks And Edge Cases

The main risk is cleanup ordering in tests that combine providers, consumers, and OF overlays. Tests should register dependent resources in an order that lets KUnit unwind safely. `clk_hw_get_clk_prepared_enabled_kunit()` returns `ERR_PTR(ret)` if prepare/enable fails after a managed get has already been registered; the get cleanup still runs at test exit because the prior wrapper succeeded. Callers must keep standard `IS_ERR()` handling for all returned clock pointers.

## Test Signals

This file is itself infrastructure for the clock KUnit suites. Its correctness is indirectly exercised by the broad set of tests in `clk_test.c`; failures would normally appear as leaked providers, stale OF providers, unbalanced prepare/enable counts, or use-after-unregister behavior between tests.
