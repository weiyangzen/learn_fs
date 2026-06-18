# sources/distributed-fs/ceph-client/drivers/spi/Kconfig

## Purpose

`drivers/spi/Kconfig` defines the build-time configuration surface for the Linux SPI subsystem in this source tree. It starts with the top-level `menuconfig SPI`, gates master-side and slave-side options, and lists controller drivers, protocol drivers, multiplexers, and offload triggers.

For this subset, the important entries are the local controller options matched by adjacent source files: `SPI_AIROHA_SNFI`, `SPI_ALTERA`, `SPI_ALTERA_CORE`, `SPI_ALTERA_DFL`, `SPI_ATMEL_QUADSPI`, `SPI_AMD`, `SPI_AMLOGIC_SPIFC_A1`, `SPI_AMLOGIC_SPIFC_A4`, and `SPI_AMLOGIC_SPISG`.

## Important APIs, types, and configuration symbols

- `SPI` is the root option and depends on `HAS_IOMEM`.
- `SPI_MASTER` defaults to `SPI` and gates most host/controller drivers.
- `SPI_MEM` enables the high-level SPI memory operation interface used by flash-focused controllers.
- `SPI_OFFLOAD` and `SPI_OFFLOAD_TRIGGER_*` provide offload support.
- `SPI_SLAVE` gates target-mode protocol handlers.
- `SPI_DYNAMIC` is selected for dynamic enumeration environments such as ACPI, OF dynamic, or SPI slave.
- Controller options express their hardware dependencies with `depends on`, `select`, `imply`, and help text. For example, `SPI_ALTERA` selects `SPI_ALTERA_CORE` and `REGMAP_MMIO`; `SPI_ALTERA_DFL` depends on `FPGA_DFL`; `SPI_ATMEL_QUADSPI` depends on `ARCH_AT91 || COMPILE_TEST` plus OF/IOMEM; `SPI_AMD` depends on PCI and SPI-MEM.

## Control flow

Kconfig has declarative control flow. Enabling `SPI` exposes the master and slave submenus. Enabling a specific controller causes its object to be selected in the SPI Makefile and may also select library code. The `if SPI_MASTER`, `if SPI_DESIGNWARE`, `if SPI_SLAVE`, and `if SPI_OFFLOAD` blocks limit which options are visible and buildable.

The list is alphabetically organized for controller drivers, and comments mark where new master and protocol entries should be added. This ordering matters for maintainability rather than runtime behavior.

## State and persistence behavior

The persistent state is the generated kernel configuration (`.config`) and the resulting built-in/module selection. Kconfig state determines which C files are compiled and whether they become built-in objects or loadable modules. There is no runtime state in this file.

## Dependencies and integration points

This file integrates with `drivers/spi/Makefile`, which maps each `CONFIG_SPI_*` symbol to one or more object files. It also integrates with architecture symbols (`ARCH_MESON`, `ARCH_AT91`, `ARCH_AIROHA`, `ARCH_STM32`, and many others), subsystem symbols (`PCI`, `OF`, `HAS_DMA`, `RESET_CONTROLLER`, `MFD_*`, `FPGA_DFL`, `MTD`), and common SPI framework options.

Driver help text documents whether an implementation supports generic SPI messages, only `spi-mem`, DMA, target mode, or special hardware sequencing restrictions.

## Risks and edge cases

- Missing `depends on SPI_MEM` for a `spi-mem`-only driver can allow invalid configurations; several drivers rely on included APIs and should stay aligned with their C code.
- Over-broad dependencies can hide useful `COMPILE_TEST` coverage; under-broad dependencies can break randconfig builds.
- `select` bypasses dependency checks of selected symbols, so it should remain limited to library-style options.
- `SPI_AMD` currently depends on `PCI` even though `spi-amd.c` also has an ACPI platform driver path and `spi-amd-pci.c` is a separate PCI front-end. That coupling is worth keeping in mind when testing platform-only builds.
- Options with help text saying "does not support generic SPI" should match their controller callbacks in C (`mem_ops` only versus `transfer_one_message`).

## Test signals

Test signals are Kconfig and build oriented: `allyesconfig`, `allmodconfig`, `randconfig`, and targeted builds for Airoha, Amlogic, Altera, AMD, and Atmel options. Verify that each enabled symbol produces the expected object names from the Makefile and that impossible configurations fail at Kconfig time rather than compile time.
