# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-clkout.c

## Purpose

`clk-exynos-clkout.c` registers the Exynos PMU clock-output control as a single composite clock named `clkout`. The clock combines a mux selecting one of up to 32 PMU-provided `clkoutN` parents with a gate controlled by the PMU debug register. Exynos4 variants use a 4-bit mux mask; Exynos5 variants use a 5-bit mask.

## Important APIs, types, and functions

- `struct exynos_clkout` embeds `struct clk_gate`, `struct clk_mux`, a spinlock, mapped PMU register base, provider node, saved PMU debug value, and onecell provider data.
- `struct exynos_clkout_variant` stores the mux mask.
- `exynos_clkout_ids` maps parent PMU compatibles to Exynos4/Exynos5 variants.
- `exynos_clkout_match_parent_dev()` ensures the device is an MFD child and matches its parent PMU compatible.
- `exynos_clkout_probe()` discovers `clkout0` through `clkout31` parents, maps PMU registers, registers the composite clock, and publishes an OF provider.
- `exynos_clkout_remove()` removes the provider, unregisters the clock, and unmaps registers.
- `exynos_clkout_suspend()` / `exynos_clkout_resume()` save and restore the PMU debug register.

## Control flow

The driver is instantiated as a child of an Exynos PMU MFD device. Probe allocates `exynos_clkout`, obtains the variant by manually matching the parent device, and uses the child OF node or parent PMU node for provider and parent lookup. It scans `clkout0` through `clkout31`; missing parents become `"none"`, and `parent_count` becomes the highest present index plus one.

Probe maps the PMU register region, points both mux and gate at `EXYNOS_PMU_DEBUG_REG`, and registers a composite `clkout` clock with mux ops and gate ops. Flags allow rate propagation to the selected parent while preventing automatic reparenting. Provider-add failure unregisters the composite clock, unmaps registers, and releases parent clocks.

## State and persistence behavior

Per-instance state is stored in the devm-allocated `exynos_clkout` attached to the platform device. The PMU debug register contains mux and gate state; the full register value is saved on suspend and restored on resume. The mux and gate share a spinlock because they modify the same register.

Parent clocks obtained during successful probe are not released in remove, while failure paths do release them. This should be reviewed if unload/reprobe behavior matters.

## Dependencies

The driver depends on PMU MFD child instantiation, supported parent PMU compatible strings, `clkoutN` parent clocks in the PMU node, OF MMIO mapping, CCF composite clock registration, and PM callbacks.

## Risks and edge cases

- Probe fails without a parent device or supported PMU compatible.
- Holes in `clkoutN` definitions are exposed as `"none"` parents to preserve mux indices.
- `of_iomap()` is not devm-managed, so `iounmap()` must remain balanced.
- Restoring the full PMU debug register can overwrite bits changed by another owner during suspend.
- Parent clock references are not put on successful remove.

## Test signals

Test by probing under each supported PMU compatible, confirming `clkout` provider registration, switching mux parents, toggling the gate, and observing physical output where available. Suspend/resume should preserve parent and gate state. Negative tests should cover missing parent device, unsupported PMU compatible, no `clkoutN` parents, and provider-add failure unwind.
