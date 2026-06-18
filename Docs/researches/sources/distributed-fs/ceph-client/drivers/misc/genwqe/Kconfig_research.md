# sources/distributed-fs/ceph-client/drivers/misc/genwqe/Kconfig

## Purpose
Kconfig entry for the IBM GenWQE PCIe accelerator driver and its platform recovery option.

## Important APIs, Types, And Functions
`menuconfig GENWQE` controls whether the GenWQE driver is built as disabled/built-in/module. It depends on `PCI` and `64BIT` and selects `CRC_ITU_T`. `config GENWQE_PLATFORM_ERROR_RECOVERY` controls whether the driver attempts platform recovery procedures, defaulting to enabled on PPC64 and disabled elsewhere.

## Control Flow
The build system includes the GenWQE objects when `CONFIG_GENWQE` is enabled. `CONFIG_GENWQE_PLATFORM_ERROR_RECOVERY` is consumed by `card_base.c` to initialize `cd->use_platform_recovery`, which changes fatal health-monitor behavior by attempting platform/fundamental reset recovery before giving up.

## State, Persistence, And Dependencies
No runtime state is stored here. It defines compile-time dependencies and defaults. The `CRC_ITU_T` selection supports code in the broader GenWQE module, and `PCI && 64BIT` reflects hardware and DMA assumptions.

## Integration Points
The help text points users to `include/linux/genwqe/genwqe_card.h` for the userspace interface. The platform recovery integer is surfaced indirectly through driver behavior and can be overridden at runtime through driver debugfs state in `struct genwqe_dev`.

## Risks
Non-PPC64 defaults disable platform recovery, so fatal MMIO failures may require external unbind/rebind or PCI recovery. Enabling a PCI accelerator driver with a world-writable device node has security implications handled elsewhere, not in Kconfig.

## Test Signals
Validate build combinations for `GENWQE=m`, `GENWQE=y`, disabled PCI, non-64-bit targets, PPC64 default recovery, and non-PPC default recovery. Confirm `CRC_ITU_T` is selected when the driver builds.
