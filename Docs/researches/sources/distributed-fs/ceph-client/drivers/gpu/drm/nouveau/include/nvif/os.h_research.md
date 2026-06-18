# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/os.h

## Purpose
Provides the kernel OS include surface and native-endian IO helper aliases used by NVIF code.

## Important APIs, Types, And Functions
Includes Linux kernel headers for types, devices, PCI/platform, firmware, I2C, delays, IO mapping, ACPI, PM, regulators, AGP, reset, IOMMU, OF, unaligned access, and Tegra SoC helpers. Defines endian-aware `ioread16/32_native`, `iowrite16/32_native`, and `iowrite64_native`.

## Control Flow
Only `iowrite64_native` has macro control flow: it writes low 32 bits then high 32 bits using native-endian 32-bit writes.

## State And Persistence
No state is stored. IO writes mutate hardware registers through caller-provided mapped addresses.

## Dependencies And Integration Points
Included by most NVIF headers and shared with object/device MMIO helpers.

## Risks
The 64-bit write order matters for hardware registers. Broad includes can hide missing direct dependencies or create build issues on non-Tegra configurations.

## Test Signals
Cross-endian build coverage, MMIO register access tests, and sparse/build warnings validate behavior.
