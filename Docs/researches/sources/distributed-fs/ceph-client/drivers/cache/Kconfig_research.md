# sources/distributed-fs/ceph-client/drivers/cache/Kconfig

## Purpose
This Kconfig file defines cache-maintenance driver options for noncoherent DMA and memory-hotplug-like coherency operations.

## Important APIs, Types, And Functions
It introduces `CACHEMAINT_FOR_DMA`, `AX45MP_L2_CACHE`, `SIFIVE_CCACHE`, `STARFIVE_STARLINK_CACHE`, `CACHEMAINT_FOR_HOTPLUG`, and `HISI_SOC_HHA`. The symbols select or depend on architecture features such as `RISCV`, `RISCV_NONSTANDARD_CACHE_OPS`, `RISCV_DMA_NONCOHERENT`, `GENERIC_CPU_CACHE_MAINTENANCE`, `ARM64`, and `ACPI`.

## Control Flow
Menu visibility is split into two groups. RISC-V noncoherent DMA cache-maintenance drivers are enabled under `CACHEMAINT_FOR_DMA`, which defaults to yes on RISC-V. The HiSilicon HHA driver is visible under `CACHEMAINT_FOR_HOTPLUG` when generic CPU cache maintenance is available.

## State And Persistence
The file contributes build-time configuration only. It indirectly controls whether cache operation registration code is built into the kernel or as a module.

## Dependencies And Integration Points
The Kconfig choices feed `drivers/cache/Makefile` and decide whether platform-specific cache maintenance objects are compiled. Selections are important because the corresponding C files register with RISC-V nonstandard cache ops or the generic cache coherency framework.

## Risks And Edge Cases
Overbroad defaults can build platform drivers on systems with no matching hardware, but early init/probe paths generally return `-ENODEV`. Missing `select` dependencies would produce link errors or disabled registration paths. `SIFIVE_CCACHE` is limited to SiFive and StarFive architectures while compatible strings include additional SoCs, so portability depends on architecture Kconfig coverage.

## Test Signals
Configuration tests should build all symbols enabled, all disabled, module build for `HISI_SOC_HHA`, COMPILE_TEST coverage, and RISC-V kernels with each nonstandard cache driver individually selected.
