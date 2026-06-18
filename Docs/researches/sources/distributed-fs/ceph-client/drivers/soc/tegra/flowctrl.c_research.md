# sources/distributed-fs/ceph-client/drivers/soc/tegra/flowctrl.c

## Purpose

`flowctrl.c` manages the Tegra flow controller used on older Tegra SoCs for CPU halt and power-gating entry/exit sequences.

## Important APIs, Types, and Functions

Global MMIO state is `tegra_flowctrl_base`. Offset arrays map CPU ids to halt and CSR registers. Public functions are `flowctrl_read_cpu_csr()`, `flowctrl_write_cpu_csr()`, `flowctrl_write_cpu_halt()`, `flowctrl_cpu_suspend_enter()`, and `flowctrl_cpu_suspend_exit()`. `tegra_flowctrl_probe()` remaps the controller through the platform driver. `tegra_flowctrl_init()` performs early mapping from DT or a 32-bit fallback physical address.

## Control Flow

Early init checks `soc_is_tegra()`, finds a compatible flowctrl node, or falls back to `0x60007000` on 32-bit Tegra if no node exists. It ioremaps the resource so low-level CPU suspend code can run before the platform driver probes. Later, the built-in platform driver remaps via devm and unmaps the early mapping. Suspend enter reads the target CPU CSR, clears WFE/WFI bitmaps according to chip id, chooses WFE for Tegra20 and Tegra30 and WFI for Tegra114/124, sets interrupt/event flags and enable, writes the CSR, then clears event/interrupt flags on other CPUs. Suspend exit clears power-gating enable and WFE/WFI selection.

## State and Persistence Behavior

The mapped base pointer persists globally. Hardware CSR/halt writes persist in the flow controller until updated. No heap state is allocated beyond managed mapping.

## Dependencies and Integration Points

It depends on OF address parsing, platform resources, Tegra chip-id fuse helpers, CPU masks, and `soc/tegra/flowctrl.h` register definitions. It integrates with CPU idle/suspend and power-gating paths.

## Risks and Edge Cases

Offset arrays cover four CPUs; callers must not pass larger CPU ids. Functions warn and no-op if called before initialization. The early fallback mapping is ARM-only and hard-coded. The platform probe unmaps the old base after replacing it, so call ordering during probe must avoid concurrent flowctrl users.

## Test Signals

Test early init with DT node, 32-bit fallback, and Tegra186+ no-flowctrl path. Exercise CPU suspend/resume on Tegra20/30/114/124, CPU hotplug, and invalid initialization ordering. Inspect CSR bits around suspend.
