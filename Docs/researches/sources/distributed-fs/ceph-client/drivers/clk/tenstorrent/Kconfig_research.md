# sources/distributed-fs/ceph-client/drivers/clk/tenstorrent/Kconfig

## Purpose

This Kconfig entry exposes the Tenstorrent Atlantis PRCM clock controller driver as `CONFIG_TENSTORRENT_ATLANTIS_PRCM`. It controls compilation of the Atlantis PRCM clock provider.

## Important APIs, Types, And Functions

The symbol is a `tristate` named "Support for Tenstorrent Atlantis PRCM Clock Controller". It depends on `ARCH_TENSTORRENT || COMPILE_TEST`, defaults to `ARCH_TENSTORRENT`, and selects `REGMAP_MMIO`, `AUXILIARY_BUS`, and `MFD_SYSCON`.

## Control Flow

When enabled, the corresponding Makefile builds `atlantis-prcm.o`. On real Tenstorrent builds the default follows the architecture selection; on other architectures it is available only for compile testing.

## State And Persistence Behavior

There is no runtime state in this file. It determines whether the driver and its selected dependencies are part of the kernel image or module set.

## Dependencies And Integration Points

The selected dependencies match the driver's MMIO regmap use and auxiliary-device reset registration. The help text says the controller covers RCPU, HSIO, MMIO, and PCIe domains, although the current source in this subset registers the RCPU-compatible data.

## Risks And Edge Cases

Because the symbol selects auxiliary bus and syscon support, dependency drift in the driver must be reflected here. If future Atlantis domains are added without Kconfig help or dependency updates, builds may succeed but DT users can fail to bind needed reset or regmap helpers.

## Test Signals

Run `allyesconfig` or `COMPILE_TEST` builds with this symbol as module and built-in. On Tenstorrent configs, verify it defaults on and that `atlantis-prcm.o` is included.
