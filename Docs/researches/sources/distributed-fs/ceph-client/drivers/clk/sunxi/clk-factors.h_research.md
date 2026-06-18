# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-factors.h

## Purpose
This header defines the data contract for legacy sunxi factor clocks.

## Important APIs, Types, And Functions
Important types are `clk_factors_config`, `factors_request`, `factors_data`, and `clk_factors`, plus registration and unregister prototypes.

## Control Flow
There is no runtime flow in the header. Provider files fill `factors_data` callbacks and bitfield tables that `clk-factors.c` consumes.

## State And Persistence
State fields describe bit shifts/widths, requested and computed factors, optional mux/gate settings, callbacks, register pointer, and cleanup pointers.

## Dependencies And Integration Points
It depends on CCF and spinlocks. Integration is with legacy providers such as `clk-mod0.c` and old PLL/module clock code.

## Risks
The sentinel `SUNXI_FACTORS_NOT_APPLICABLE` is zero, so width zero means absent. Callback authors must return raw register field values, not always arithmetic factors.

## Test Signals
Build plus rate tests for each legacy factor user validate this API.
