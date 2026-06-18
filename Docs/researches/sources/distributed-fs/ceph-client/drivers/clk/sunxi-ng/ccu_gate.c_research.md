# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_gate.c

## Purpose
`ccu_gate.c` implements sunxi-ng gate clocks and reusable gate bit helpers for compound clock classes.

## Important APIs, Types, And Functions
Important APIs are `ccu_gate_helper_disable()`, `ccu_gate_helper_enable()`, `ccu_gate_helper_is_enabled()`, and exported `ccu_gate_ops`. The ops also support all-parent predivider rate propagation for gate-only derived clocks.

## Control Flow
Enable/disable/read paths update or read a single bit under the shared lock, optionally setting `CCU_SUNXI_UPDATE_BIT` before writes. Rate callbacks either pass through the parent rate or account for `CCU_FEATURE_ALL_PREDIV`.

## State And Persistence
Only hardware gate bits are state. No persistence or caching is used.

## Dependencies And Integration Points
It depends on CCF, MMIO, `ccu_common`, and is used by nearly every class and SoC provider for simple bus/module gates.

## Risks
A missing update bit can cause writes not to latch on some SoCs. A zero gate means always enabled, so callers must distinguish intentional zero from missing descriptor data.

## Test Signals
Test with clock prepare/enable/disable cycles, clk-summary gate state, and peripheral probe/suspend paths that rely on bus gates.
