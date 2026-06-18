# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/core.h

## Purpose
This private SoCFPGA header declares reset-manager offsets, reset bits, OCRAM/SDRAM globals, ECC init functions, and SMP trampoline symbols shared by the platform files.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `socfpga_init_l2_ecc`, `socfpga_init_ocram_ecc`, `socfpga_init_arria10_l2_ecc`, `socfpga_init_arria10_ocram_ecc`, `socfpga_sdram_self_refresh`.
- Register/constant macro families: `SOCFPGA`(7), `RSTMGR`(3), `__MA`(1); examples: `__MACH_CORE_H`, `SOCFPGA_RSTMGR_CTRL`, `SOCFPGA_RSTMGR_MODMPURST`, `SOCFPGA_RSTMGR_MODPERRST`, `SOCFPGA_RSTMGR_BRGMODRST`, `SOCFPGA_A10_RSTMGR_CTRL`, `SOCFPGA_A10_RSTMGR_MODMPURST`, `RSTMGR_CTRL_SWCOLDRSTREQ`, `RSTMGR_CTRL_SWWARMRSTREQ`, `RSTMGR_MPUMODRST_CPU1`, `SOCFPGA_SCU_VIRT_BASE`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; suspend paths persist resume vectors and controller state across low-power entry. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (1154 bytes, 43 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
