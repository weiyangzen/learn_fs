<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mellanox/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/mellanox/Kconfig

## Purpose

This Kconfig file defines platform support options for Mellanox/Nvidia systems, switches, line cards, BlueField SoCs, and the Nvidia SN2201 platform.

## Important APIs, Types, And Functions

`MELLANOX_PLATFORM` gates the menu for X86, ARM, ARM64, or compile testing. Feature symbols include `MLX_PLATFORM`, `MLXREG_DPU`, `MLXREG_HOTPLUG`, `MLXREG_IO`, `MLXREG_LC`, `MLXBF_TMFIFO`, `MLXBF_BOOTCTL`, `MLXBF_PMC`, and `NVSW_SN2201`. Dependencies select or require ACPI, I2C, PCI, HWMON, REGMAP, REGMAP_I2C, ARM64, NET, and virtio console/net.

## Control Flow

Enabling the top-level menu exposes individual platform drivers. Each symbol controls a separate source module under `drivers/platform/mellanox`, ranging from x86 platform support to BlueField firmware/monitoring and switch-management drivers.

## State And Persistence

No runtime state is defined here. The options determine which hardware-management drivers may run.

## Dependencies And Integration Points

It integrates Mellanox platform code with ACPI/I2C/PCI discovery, regmap-backed device register access, hwmon, virtio, networking, and BlueField ARM64 support.

## Risks

Dependencies are hardware-specific; overly broad compile-test exposure can reveal missing stubs, while overly narrow dependencies can hide usable drivers. Some help text refers to Nvidia-rebranded hardware but symbols retain Mellanox naming, so user-facing config clarity matters.

## Test Signals

Check Kconfig visibility across X86/ARM/ARM64/COMPILE_TEST, dependency selections, allmodconfig builds, and each symbol's object linkage in the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mellanox/Kconfig -->
