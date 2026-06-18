# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_common.c

## Purpose
`ccu_common.c` is the registration and shared utility layer for sunxi-ng clock controller providers. It wires descriptor arrays into Linux CCF, registers reset controllers, provides PLL lock waiting, rate comparison policy, and PLL notifier support.

## Important APIs, Types, And Functions
Important APIs are `ccu_helper_wait_for_lock()`, `ccu_is_better_rate()`, `ccu_pll_notifier_register()`, `devm_sunxi_ccu_probe()`, and `of_sunxi_ccu_probe()`. Internally `sunxi_ccu_probe()` initializes shared locks/base pointers, registers each `clk_hw`, installs the onecell provider, and registers `ccu_reset_ops`.

## Control Flow
Probe-style callers pass a mapped register base and `sunxi_ccu_desc`. The helper sets each `ccu_common` base/lock, registers clock hardware, applies rate ranges, adds the OF provider, then registers reset controls. Managed probe stores a release callback that unregisters resets, provider, and clocks.

## State And Persistence
It stores a small `struct sunxi_ccu` allocation for descriptor, spinlock, and reset-controller state during the provider lifetime. There is no disk persistence; hardware state is the register contents modified by the registered clocks/resets.

## Dependencies And Integration Points
Dependencies include CCF, OF providers, reset-controller core, iopoll, module support, and adjacent `ccu_gate`/`ccu_reset` helpers. Every sunxi-ng SoC CCU provider integrates through this file.

## Risks
Failure unwinding must unregister only clocks already registered. Lock wait timeouts warn but do not recover hardware. Rate comparison behavior affects every factor search, so closest-vs-not-above semantics must be changed cautiously.

## Test Signals
Test with builds for multiple sunxi-ng providers, probe/unbind where supported, reset-controller registration, clean failure injection if possible, and runtime checks that onecell clock lookups and reset operations work.
