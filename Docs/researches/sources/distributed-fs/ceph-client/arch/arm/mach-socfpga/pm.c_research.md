# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/pm.c

## Purpose
This file implements SoCFPGA suspend-to-RAM support by copying a DDR self-refresh routine into OCRAM and invoking it from cpu_suspend while outer cache is disabled.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `socfpga_setup_ocram_self_refresh`, `socfpga_pm_suspend`, `socfpga_pm_enter`.
- Initcall hooks: `socfpga_pm_init`.

## Control Flow
Suspend control flow registers platform suspend operations at init time. On suspend, the code prepares resume vectors and controller state, enters `cpu_suspend()` or a platform low-power path, and on wake restores cache/coherency or controller state before returning to generic PM.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles; suspend paths persist resume vectors and controller state across low-power entry; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/bitops.h`, `linux/genalloc.h`, `linux/init.h`, `linux/io.h`, `linux/of.h`, `linux/of_platform.h`, `linux/platform_device.h`, `linux/suspend.h`, `asm/suspend.h`, `asm/fncpy.h`, `core.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with platform-device/resource registration and legacy board data handoff.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `pm.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (3196 bytes, 142 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
