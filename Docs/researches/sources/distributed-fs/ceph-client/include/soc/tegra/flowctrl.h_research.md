# sources/distributed-fs/ceph-client/include/soc/tegra/flowctrl.h

## Purpose

`flowctrl.h` defines Tegra flow-controller register offsets, bit masks, and optional APIs for CPU halt, WFE/WFI, suspend entry, and suspend exit handling.

## Important APIs, Types, and Functions

Constants cover CPU halt event registers, wait modes, JTAG/SCLK resume bits, IRQ/FIQ halt masks, CPU CSR registers, interrupt/event flags, external rail enable bits, and Tegra20/Tegra30 WFE/WFI bitmaps. With `CONFIG_SOC_TEGRA_FLOWCTRL`, C users get `flowctrl_read_cpu_csr()`, `flowctrl_write_cpu_csr()`, `flowctrl_write_cpu_halt()`, `flowctrl_cpu_suspend_enter()`, and `flowctrl_cpu_suspend_exit()`. Disabled builds stub these out.

## Control Flow

Power-management code writes CPU halt and CSR values before low-power entry and calls suspend enter/exit helpers around CPU suspend. Register state drives wake and resume behavior.

## State and Persistence

State is in flow-controller hardware registers. The header only defines constants and call signatures.

## Dependencies and Integration Points

The header is assembly-safe and hides C declarations under `!__ASSEMBLY__`. It integrates with Tegra ARM suspend, CPU hotplug, cpuidle, and secondary CPU bring-up paths.

## Risks

Incorrect masks can halt the wrong CPU, block wake sources, or break resume. Changes must remain safe for assembly inclusion.

## Test Signals

Exercise SMP boot, CPU hotplug, LP2/suspend entry and exit, IRQ/FIQ wake behavior, and builds without `CONFIG_SOC_TEGRA_FLOWCTRL`.
