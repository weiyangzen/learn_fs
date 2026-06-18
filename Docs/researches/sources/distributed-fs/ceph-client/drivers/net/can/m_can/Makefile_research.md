# sources/distributed-fs/ceph-client/drivers/net/can/m_can/Makefile

## Purpose
This Makefile maps the M_CAN Kconfig symbols to build artifacts.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_CAN_M_CAN) += m_can.o` builds the common class driver.
- `obj-$(CONFIG_CAN_M_CAN_PCI) += m_can_pci.o` builds the PCI wrapper.
- `obj-$(CONFIG_CAN_M_CAN_PLATFORM) += m_can_platform.o` builds the platform/MMIO wrapper.
- `obj-$(CONFIG_CAN_M_CAN_TCAN4X5X) += tcan4x5x.o` builds a composite TCAN module from `tcan4x5x-core.o` and `tcan4x5x-regmap.o`.

## Control Flow
Kbuild includes the listed objects according to resolved Kconfig values. The TCAN target is a multi-object module, so both core probe logic and SPI regmap transport are linked together.

## State And Persistence
There is no runtime state. The file defines build composition.

## Dependencies And Integration Points
The common `m_can.o` exports class APIs consumed by all wrappers. The TCAN module depends on both `tcan4x5x-core.c` and `tcan4x5x-regmap.c` and on the Kconfig-selected regmap SPI support.

## Risks And Edge Cases
- Building a wrapper without compatible exported symbols from `m_can.o` would fail at link/modpost time, so symbol visibility in `m_can.c` is part of the build contract.
- The empty initial `tcan4x5x-objs :=` is harmless but means later object additions define the full composite module.

## Test Signals
Verify `make M=drivers/net/can/m_can` for built-in and module configs, and check that `tcan4x5x.ko` contains both TCAN object files.
