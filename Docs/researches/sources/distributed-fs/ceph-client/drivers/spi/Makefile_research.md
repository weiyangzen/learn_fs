# sources/distributed-fs/ceph-client/drivers/spi/Makefile

## Purpose

`drivers/spi/Makefile` maps SPI Kconfig symbols to object files. It builds the SPI core (`spi.o`), SPI memory support (`spi-mem.o`), mux/offload/protocol helpers, and the large set of controller drivers.

For this subset, it connects `CONFIG_SPI_AIROHA_SNFI` to `spi-airoha-snfi.o`, Altera symbols to the platform/core/DFL objects, Amlogic symbols to the A1/A4/SPISG drivers, `CONFIG_SPI_ATMEL_QUADSPI` to `atmel-quadspi.o`, and `CONFIG_SPI_AMD` to both `spi-amd.o` and `spi-amd-pci.o`.

## Important APIs, types, and build rules

- `ccflags-$(CONFIG_SPI_DEBUG) := -DDEBUG` enables debug logging in SPI drivers when `SPI_DEBUG` is selected.
- `obj-$(CONFIG_SPI_MASTER) += spi.o` builds the controller/core translation layer.
- `obj-$(CONFIG_SPI_MEM) += spi-mem.o` builds the high-level SPI memory API.
- Per-driver `obj-$(CONFIG_...) += file.o` lines bind configuration choices to compilation units.
- Composite objects are used for some shared implementations, such as `spi-dw-y`, `spi-octeon-objs`, `spi-thunderx-objs`, and `spi-pxa2xx-core-y`.

## Control flow

The kernel build system evaluates each `obj-*` assignment after Kconfig resolves symbols. Built-in symbols produce built-in objects; module symbols produce modules. Multi-object driver entries are linked together according to kbuild rules.

For AMD, `CONFIG_SPI_AMD` builds both the common/platform driver object and the PCI bridge front-end object. For Altera, separate symbols let platforms build either the generic platform wrapper or the DFL wrapper while sharing `spi-altera-core.o`.

## State and persistence behavior

The file has no runtime state. Its persistent effect is the build artifact layout under the kernel build directory and module set. The mapping must remain synchronized with both Kconfig symbol names and source filenames.

## Dependencies and integration points

The Makefile integrates directly with `drivers/spi/Kconfig`, the top-level kernel kbuild system, module linking, and C source module metadata. It also encodes source organization decisions, such as shared cores versus bus-specific wrappers.

## Risks and edge cases

- Kconfig symbols and object names must stay synchronized. A rename in either file can silently omit a driver or break builds.
- Multi-object mappings must include all needed objects. The AMD line links both `spi-amd.o` and `spi-amd-pci.o`; changing this could drop PCI support.
- Shared-core arrangements rely on Kconfig `select` relationships. For example, `SPI_ALTERA` and `SPI_ALTERA_DFL` must continue to select `SPI_ALTERA_CORE`.
- Alphabetical ordering is a maintainer convention; misplaced additions increase merge conflict risk.

## Test signals

Targeted build tests should enable each symbol in this subset and confirm the expected object is compiled. `make W=1 drivers/spi/` with representative configs, plus `allmodconfig`, catches missing object names and duplicate or stale kbuild entries.
