# sources/distributed-fs/ceph-client/drivers/clk/clk.h

## Purpose

`clk.h` is a small internal header for the clock framework implementation and adjacent helpers. It exposes framework-private entry points needed by code that cannot use only the public consumer/provider headers, notably OF-to-`clk_hw` lookup, clkdev hardware lookup, creation of a consumer `struct clk` from a provider `struct clk_hw`, and the internal put path.

## Important APIs, Types, And Functions

The header forward-declares `struct clk_hw`, `struct device`, and `struct of_phandle_args`. When both `CONFIG_OF` and `CONFIG_COMMON_CLK` are enabled, it declares `of_clk_get_hw(struct device_node *np, int index, const char *con_id)`. Otherwise it provides an inline stub returning `ERR_PTR(-ENOENT)`, allowing callers to compile without large ifdef blocks.

It declares `clk_find_hw(const char *dev_id, const char *con_id)`, which is implemented outside this file and used by `clk.c` parent resolution as a clkdev fallback. Under `CONFIG_COMMON_CLK`, it declares `clk_hw_create_clk()` and `__clk_put()`. Without common clock support, `clk_hw_create_clk()` is a cast-based inline stub returning the hardware pointer as a `struct clk *`, and `__clk_put()` is a no-op.

## Control Flow

There is no runtime control flow in this header beyond compile-time feature selection. Its role is to let the same callers build whether OF/common-clock support exists. The fallback paths are intentionally simple: OF lookup fails with `-ENOENT`, clock creation degenerates to a cast in non-common-clock builds, and put does nothing.

## State And Persistence Behavior

The header owns no state and persists nothing. It only defines declarations and inline compatibility stubs.

## Dependencies And Integration Points

This file integrates the common clock core with clkdev and OF-aware lookup code. `clk.c` includes it for `clk_hw_create_clk()`, `__clk_put()`, and OF lookup declarations. KUnit tests include it because `clk_hw_get_clk()` and direct provider-to-consumer creation are internal enough that the public headers alone are not sufficient.

## Risks And Edge Cases

The primary risk is configuration skew: callers must handle `ERR_PTR(-ENOENT)` when OF or common clock support is not compiled in. The non-common-clock cast stub is deliberately a compatibility shim, so code must avoid assuming a fully functional `struct clk` object in that configuration. The header relies on other headers to provide `ERR_PTR()` and full structure definitions where needed.

## Test Signals

`clk_test.c` includes this header and directly exercises `clk_hw_create_clk()`-backed behavior through `clk_hw_get_clk()` and KUnit-managed wrappers. Build coverage across `CONFIG_OF` and `CONFIG_COMMON_CLK` combinations is the main signal for the inline stubs.
