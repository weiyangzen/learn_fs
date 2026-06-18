# subset-b-005378 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/sysfs_slave_dpn.c -->
# sources/distributed-fs/ceph-client/drivers/soundwire/sysfs_slave_dpn.c

## Purpose

`sysfs_slave_dpn.c` builds per-data-port sysfs attribute groups for SoundWire slave devices. It exposes read-only `dpN_src` and `dpN_sink` directories under the slave device, with one attribute per `struct sdw_dpn_prop` capability such as word widths, channel counts, supported channel combinations, interrupt bits, async buffer size, block-pack mode, and port encoding.

The file is metadata publication code. It does not program SoundWire hardware; it converts the discovery-time `slave->prop.source_ports`, `slave->prop.sink_ports`, `src_dpn_prop`, and `sink_dpn_prop` arrays into sysfs files.

## Important APIs, types, and functions

- `struct dpn_attribute` embeds `struct device_attribute` and records the logical port number `N`, direction `dir`, and printf-style format string used by the generated show callback.
- `sdw_dpn_attr(field)` generates a scalar `field_show()`, a `field_dpn_show()` helper, and an allocator for each scalar DPN property.
- `sdw_dpn_array_attr(field)` does the same for variable-length arrays: `words`, `ch_combinations`, and `channels`.
- `add_all_attributes()` allocates the 15 attributes, verifies the hard-coded `SDW_DPN_ATTRIBUTES` count, creates an attribute group named `dp%d_src` or `dp%d_sink`, and registers it with `devm_device_add_group()`.
- `sdw_slave_sysfs_dpn_init()` is the exported initializer. It walks all source and sink port bits and invokes `add_all_attributes()`.

## Control flow

`sdw_slave_sysfs_dpn_init()` returns immediately when the slave has no source or sink ports. Otherwise it iterates set bits in the source-port mask and creates source groups, then does the same for sink ports. Each group contains all 15 attribute files.

At read time, a sysfs show callback recovers `struct sdw_slave` through `dev_to_sdw_dev()`, recovers the containing `struct dpn_attribute`, selects either `src_dpn_prop` or `sink_dpn_prop`, then iterates the corresponding port mask. The property-array index increments only for set ports, so bit number `N` maps to the dense DPN property entry for that advertised port.

## State and persistence behavior

All allocations are device-managed with `devm_kzalloc()`, `devm_kcalloc()`, `devm_kasprintf()`, and `devm_device_add_group()`. There is no independent persistence beyond the lifetime of the SoundWire slave device. Attribute values are read directly from `slave->prop`; if those properties changed after registration, sysfs would reflect the new in-memory values, but the normal model is static discovery data.

## Dependencies and integration points

The file depends on the SoundWire core types from `linux/soundwire/sdw.h`, `sdw_type.h`, local `bus.h`, and `sysfs_local.h`. It integrates with the slave sysfs setup path through `sdw_slave_sysfs_dpn_init()` and relies on `struct sdw_dpn_prop` layout matching the generated field names.

The sysfs ABI is the visible integration point: userspace can inspect per-port capability files under `dpN_src` and `dpN_sink`, while kernel code consumes only the initializer.

## Risks and edge cases

- `SDW_DPN_ATTRIBUTES` is manually maintained. The local mismatch check catches the final count, but only after allocation attempts.
- The array properties are printed one value per line and then an extra newline. Consumers should treat them as lists rather than single scalar values.
- The dense property-array indexing assumes the property arrays are ordered exactly by ascending set bits in `source_ports` and `sink_ports`.
- The generated show callbacks return `-EINVAL` if a group's recorded port number no longer appears in the mask. That should not happen in normal use.
- The code uses `sprintf()` into sysfs buffers. Values are small, but future larger arrays should keep sysfs page-size limits in mind.

## Test signals

Useful checks are compile coverage for `CONFIG_SOUNDWIRE`, boot/probe coverage with SoundWire slaves that advertise multiple sparse source and sink ports, and sysfs inspection confirming each `dpN_*` group contains exactly the 15 expected files. Negative tests should cover devices with no DPN ports and sparse masks such as ports 1 and 7 to validate property-array indexing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soundwire/sysfs_slave_dpn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/Kconfig -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/Makefile -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/atmel-quadspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/atmel-quadspi.c

## Purpose

`atmel-quadspi.c` is a platform SPI memory controller driver for Atmel/Microchip QSPI and OSPI blocks. It implements `spi_controller_mem_ops` rather than generic SPI message transfer and is intended for memory-like devices such as SPI NOR, SPI NAND, Octal SPI flash, and related serial memories.

The driver covers older SAMA5D2/SAM9X60 style QSPI registers and newer SAMA7G5/SAM9X7/SAMA7D65 variants with generic clock, read/write instruction-code registers, octal/DTR support, DMA, DLL, and pad calibration.

## Important APIs, types, and functions

- `struct atmel_qspi_caps` describes per-compatible hardware capabilities: `max_speed_hz`, `has_qspick`, `has_gclk`, `has_ricr`, `octal`, `has_dma`, `has_2xgclk`, `has_padcalib`, and `has_dllon`.
- `struct atmel_qspi` stores mapped register and AHB memory windows, clocks, capability and operation tables, completions, DMA channels, cached mode/clock registers, and AHB mapping size.
- `struct atmel_qspi_ops` selects variant-specific `set_cfg()` and `transfer()` functions.
- `atmel_qspi_supports_op()` validates SPI-MEM operations against bus-width modes and hardware quirks.
- `atmel_qspi_set_cfg()` handles legacy QSPI instruction-frame programming, including 1/2/3/4-byte address cases and the 16-bit address workaround.
- `atmel_qspi_sama7g5_set_cfg()` programs the newer RICR/WICR/IFR path, DTR flags, octal protocol type, and write-access count.
- `atmel_qspi_transfer()` and `atmel_qspi_sama7g5_transfer()` move data through the memory-mapped AHB window, optionally using DMA on newer parts.
- `atmel_qspi_exec_op()` enforces AHB window bounds, resumes runtime PM, programs config, transfers, and autosuspends.
- `atmel_qspi_setup()`, `atmel_qspi_set_cs_timing()`, and SAMA7G5 helpers manage speed, clock rate, CS timing, DLL, and pad calibration.

## Control flow

Probe allocates a SPI controller, reads OF match capabilities, maps `qspi_base` and `qspi_mmap`, obtains clocks, optionally initializes DMA, requests the IRQ, enables runtime PM, initializes the controller, and registers with the SPI core.

Runtime SPI-MEM flow is:

1. SPI core calls `supports_op()` and possibly `adjust_op_size()` at the framework level.
2. `exec_op()` checks the memory-window bounds and address size, resumes the device, and calls the selected `set_cfg()`.
3. `set_cfg()` translates `spi_mem_op` fields into IAR/ICR/IFR or RICR/WICR/IFR registers and serial-memory mode.
4. `transfer()` either waits for command completion for no-data commands, copies through the AHB aperture, or uses DMA for large SAMA7G5 read/write data operations.
5. The IRQ handler accumulates pending status bits and completes `cmd_completion` when the desired mask is observed.

System and runtime PM disable and re-enable clocks, restore key register state, and for newer parts use `atmel_qspi_sama7g5_init()`/`suspend()` to manage QSPI enable, DLL lock, pad calibration, and generic clock.

## State and persistence behavior

Persistent hardware state includes QSPI mode register, serial clock register, instruction-frame registers, DLL/pad calibration, timeout, and clock rates. Software caches `aq->mr`, `aq->scr`, and `target_max_speed_hz` so setup and resume can restore intended behavior. The AHB memory window maps flash access; data is not stored by the driver except transiently through caller buffers and DMA mappings.

Runtime PM autosuspends after 500 ms. Device-managed allocations clean up mappings, clocks, IRQs, and DMA channels, while `remove()` unregisters the controller and disables the hardware when possible.

## Dependencies and integration points

The driver depends on platform device resources named `qspi_base` and `qspi_mmap`, clocks (`pclk`, optionally `qspick` or `gclk`), an IRQ, optional DMA channels `rx`/`tx`, OF compatible data, PM runtime, DMAengine, and the SPI-MEM framework. OF compatibles include `atmel,sama5d2-qspi`, `microchip,sam9x60-qspi`, `microchip,sama7g5-{qspi,ospi}`, `microchip,sam9x7-ospi`, and `microchip,sama7d65-{qspi,ospi}`.

## Risks and edge cases

- The AHB window bound check rejects operations that exceed `mmap_size`; there is no fallback to regular SPI mode.
- The legacy 16-bit address workaround is delicate and depends on dummy-cycle count and matching opcode/address bus widths.
- DMA is used only for newer-capability parts and large addressed transfers; DMA mapping or channel failure falls back only where code explicitly chooses PIO.
- Newer DLL and pad-calibration paths have several poll timeouts; failures can break resume or setup.
- Error paths during DMA transfer must unmap scatterlists and terminate timed-out channels correctly.
- The driver assumes one chip select (`num_chipselect = 1`), matching controller limitations.
- The source currently contains a duplicated `return ret;` in `atmel_qspi_init()` after the serial-memory-mode call; it is unreachable/no-op but worth cleaning.

## Test signals

Build with `CONFIG_SPI_ATMEL_QUADSPI` across OF/PM/DMA variants. Runtime tests should execute SPI-MEM reads, writes, erase/status no-data commands, dual/quad/octal reads where supported, 1/2/3/4-byte addresses, DMA and non-DMA transfer sizes, suspend/resume, runtime autosuspend, and clock-rate setup. Hardware register tracing should confirm LASTXFER/CSRA or CMD_COMPLETED completion paths and proper RICR/WICR use on newer SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/atmel-quadspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/internals.h -->
# sources/distributed-fs/ceph-client/drivers/spi/internals.h

## Purpose

`internals.h` is a private header for SPI core implementation files, explicitly intended for `spi.c` and `spi-mem.c` rather than controller drivers. It exposes queue flushing and DMA buffer mapping helpers that are shared inside the SPI core.

## Important APIs, types, and functions

- `spi_flush_queue(struct spi_controller *ctrl)` is declared for flushing queued controller work.
- `spi_map_buf()` and `spi_unmap_buf()` map or unmap a linear buffer into a scatter-gather table when `CONFIG_HAS_DMA` is enabled.
- Without DMA support, `spi_map_buf()` returns `-EINVAL` and `spi_unmap_buf()` is an empty inline.
- `spi_xfer_is_dma_mapped()` checks whether a transfer should be considered DMA mapped by combining `ctlr->can_dma()`, the SPI device and transfer, and the transfer's `tx_sg_mapped`/`rx_sg_mapped` flags.

## Control flow

This header does not execute by itself. It shapes compile-time behavior: DMA helpers are real declarations when the architecture has DMA support and stubs otherwise. SPI core code can call the same helper names while preserving no-DMA build coverage.

## State and persistence behavior

There is no state in the header. State affected by these helpers lives in `struct sg_table`, `struct spi_transfer`, and controller/device DMA mappings owned by caller code.

## Dependencies and integration points

The header includes `linux/device.h`, `linux/dma-direction.h`, `linux/scatterlist.h`, and `linux/spi/spi.h`. It is a SPI core internal contract and should not become a public controller-driver API.

## Risks and edge cases

- External use by controller drivers would couple them to SPI core internals.
- `spi_xfer_is_dma_mapped()` requires `ctlr->can_dma` to be non-NULL and true; mapped scatterlists alone are not enough.
- No-DMA builds intentionally fail `spi_map_buf()` with `-EINVAL`, so callers must handle that path.

## Test signals

Compile coverage with and without `CONFIG_HAS_DMA` is the key signal. SPI core DMA and PIO transfer tests should verify that mapped transfer flags are honored and no-DMA configurations still build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/internals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-airoha-snfi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-airoha-snfi.c

## Purpose

`spi-airoha-snfi.c` is a SPI-MEM controller driver for the Airoha SPI NAND Flash Interface. It provides manual FIFO command execution for generic SPI-MEM operations and optional NFI DMA direct-mapping paths for SPI NAND cache read/write operations.

The controller is split into a SPI control register block and an NFI-to-SPI register block. The driver exposes the hardware as a SPI controller with memory operations, not as a generic full-duplex SPI bus.

## Important APIs, types, and functions

- `struct airoha_snand_ctrl` stores the device, SPI control regmap, NFI regmap, and SPI clock.
- `airoha_snand_set_fifo_op()`, `*_write_data_to_fifo()`, and `*_read_data_from_fifo()` implement manual FIFO command and byte-data transfers with poll timeouts.
- `airoha_snand_set_mode()` switches between manual, DMA, and auto-ish controller modes by programming control registers.
- `airoha_snand_supports_op()` validates bus widths and distinguishes page-cache operations from generic single-lane commands.
- `airoha_snand_dirmap_create()` accepts direct maps up to `SPI_NAND_CACHE_SIZE` and only for supported op templates.
- `airoha_snand_dirmap_read()` and `airoha_snand_dirmap_write()` use the NFI DMA engine to transfer rounded cache data to/from a per-device cache buffer.
- `airoha_snand_exec_op()` sends opcode, address, dummy bytes, and data through manual FIFO mode.
- `airoha_snand_setup()` allocates a per-SPI-device `SPI_NAND_CACHE_SIZE` buffer and stores it with `spi_set_ctldata()`.

## Control flow

Probe maps two resources, creates regmaps, enables the SPI clock, optionally disables DMA on a known bad EN7523 boot strap, sets a 32-bit DMA mask, fills controller properties, initializes the NFI block, and registers the controller.

Manual operation flow switches to manual mode, lowers chip select through FIFO command, writes opcode/address/dummy segments, transfers data in chunks capped at `SPI_MAX_TRANSFER_SIZE`, and raises chip select. Direct-map read/write switches to DMA mode, resets and configures the NFI block, maps the per-device cache buffer, programs DMA address/length/opcode/mode/address registers, triggers the read or write, polls completion bits, unmaps, returns to manual mode, and copies the requested subrange.

## State and persistence behavior

The driver maintains little mutable software state beyond the regmaps, clock, and per-device cache buffer. Hardware mode persists in controller registers; both success and error paths try to return to manual mode after DMA. The direct-map buffer is device-managed and lives as long as the SPI device.

## Dependencies and integration points

The driver depends on platform resources for the two MMIO regions, a `"spi"` clock, regmap-mmio, DMA mapping, OF compatibles, and SPI-MEM. It integrates with SPI NAND through SPI-MEM direct mapping and supports cache opcodes such as read-from-cache and program-load variants.

## Risks and edge cases

- `airoha_snand_set_cs()` contains a duplicated unreachable `return`; behavior is unaffected, but it signals a cleanup opportunity.
- Direct-map reads round `offs + len` up to 64 bytes and use a fixed 4 KiB+256 cache buffer; bounds are guarded by dirmap length but should be kept aligned with SPI NAND geometry.
- EN7523 reserved boot mode disables DMA due to known data-damage risk. Tests must cover both DMA and no-DMA mem-op tables.
- DMA paths manually toggle controller modes and completion bits; error paths must always restore manual mode.
- Bus-width support is intentionally narrow for page operations and single-lane for generic commands.
- The OF match table only lists `airoha,en7581-snand`, while probe also checks `airoha,en7523-snand`; this mismatch may make the EN7523-specific branch unreachable unless matched through another compatible string.

## Test signals

Build with `CONFIG_SPI_AIROHA_SNFI`. Runtime tests should cover reset/read-id/get-feature/set-feature via manual FIFO, cache read/write through direct-map DMA, PIO fallback/no-DMA mode, dual and quad read/program-load opcodes, DMA timeout/error handling, and EN7523 strap behavior. SPI NAND MTD tests should verify data integrity across page and OOB boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-airoha-snfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-altera-core.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-altera-core.c

## Purpose

`spi-altera-core.c` is the shared transfer engine for Altera SPI controllers. It owns register-level chip-select handling, PIO transmit/receive, optional IRQ-driven completion, and host initialization. Bus-specific wrappers supply the regmap, register offset, IRQ, and controller registration.

## Important APIs, types, and functions

- Register definitions cover RX/TX data, status, control, and target-select registers.
- `altr_spi_writel()` and `altr_spi_readl()` wrap regmap accesses and add device error logging.
- `altera_spi_set_cs()` selects or deselects a chip by writing target-select and the SSO control bit.
- `altera_spi_tx_word()` and `altera_spi_rx_word()` marshal 1-, 2-, or 4-byte words between transfer buffers and hardware data registers.
- `altera_spi_txrx()` implements `host->transfer_one`, using either interrupt-driven or polling mode.
- `altera_spi_irq()` handles receive-ready interrupts and finalizes the transfer.
- `altera_spi_init_host()` assigns callbacks, disables interrupts, clears status, and flushes stale RX data.

## Control flow

For polling transfers, `altera_spi_txrx()` writes one word, spins until receive-ready, reads the word, and repeats until all words are complete, then calls `spi_finalize_current_transfer()`.

For IRQ transfers, it enables receive-ready interrupts, sends the first word, and returns `1` to indicate asynchronous completion. The IRQ handler reads the received word, writes the next word if any remain, or disables receive interrupts and finalizes the transfer.

Chip select is asserted before transfers by selecting `BIT(chipselect)` and setting SSO; it is deasserted by clearing SSO and target-select.

## State and persistence behavior

Per-transfer mutable state lives in `struct altera_spi` fields owned by the wrapper-provided controller data: `tx`, `rx`, `count`, `len`, `bytes_per_word`, `imr`, `regmap`, `regoff`, and `irq`. Hardware control state persists in the control and target-select registers until changed.

## Dependencies and integration points

The core depends on `linux/spi/altera.h` for `struct altera_spi`, the SPI framework, regmap, and exported symbols consumed by `spi-altera-platform.c` and `spi-altera-dfl.c`.

## Risks and edge cases

- Polling mode spins with `cpu_relax()` and no timeout; broken hardware can hang the transfer path.
- Only byte widths of 1, 2, and 4 are explicitly handled. Wrapper `bits_per_word_mask` must prevent unsupported widths.
- Error returns from regmap reads/writes are logged but transfer code generally continues with default values.
- Transfer length is divided by `bytes_per_word`; non-multiple lengths would truncate words and should be rejected by the SPI core or wrapper configuration.

## Test signals

Build both platform and DFL wrappers. Runtime tests should cover polling and IRQ modes, chipselect changes, 8/16/32-bit transfers, RX-only and TX-only buffers, and regmap error injection if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-altera-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-altera-dfl.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-altera-dfl.c

## Purpose

`spi-altera-dfl.c` is a Device Feature List bus wrapper for the shared Altera SPI core. It supports FPGA DFL features where an Altera SPI master is accessed through an indirect register window, commonly connected to Intel MAX BMC SPI devices.

## Important APIs, types, and functions

- `indirect_bus_reg_read()` and `indirect_bus_reg_write()` implement regmap callbacks over the DFL indirect-access registers with busy polling and `INDIRECT_TIMEOUT`.
- `indirect_regbus_cfg` describes a 32-bit regmap backed by those callbacks.
- `config_spi_host()` reads `SPI_CORE_PARAMETER` and derives mode bits, chipselect count, and bits-per-word mask.
- `dfl_spi_altera_probe()` allocates the SPI controller, maps DFL MMIO, creates the indirect regmap, initializes the shared core, registers the controller, and instantiates a board-info SPI device (`m10-n5010` or `m10-d5005`).

## Control flow

Probe maps the DFL resource, reads controller parameters, initializes a regmap whose operations issue indirect read/write commands, sets `hw->irq = -EINVAL` for polling mode, calls `altera_spi_init_host()`, and registers the controller. After controller registration it creates a MAX10 SPI device on chip select 0 with a 12.5 MHz max speed.

## State and persistence behavior

Software state is device-managed and tied to the DFL device. Hardware state persists in the indirect SPI registers and DFL feature MMIO. The wrapper does not implement remove-specific cleanup beyond devm and module DFL driver teardown.

## Dependencies and integration points

The file depends on the FPGA DFL bus, regmap, SPI framework, `linux/spi/altera.h`, and the exported core functions from `spi-altera-core.c`. It matches DFL feature ID `0xe` under `FME_ID`.

## Risks and edge cases

- Indirect read/write loops use `cpu_relax()` with a fixed loop count rather than time-based polling.
- The wrapper forces polling mode by setting a negative IRQ.
- `board_info.bus_num = 0` is hard-coded even though the controller uses `host->bus_num = -1`; this deserves validation on systems with multiple SPI buses.
- Failure to create the child SPI device is logged but does not fail probe.

## Test signals

Build with `CONFIG_FPGA_DFL` and `CONFIG_SPI_ALTERA_DFL`. Runtime tests on DFL hardware should verify indirect read/write timeouts, parameter-derived chipselect and bit-width limits, creation of the expected MAX10 device name by revision, and polling transfers through the shared core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-altera-dfl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-altera-platform.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-altera-platform.c

## Purpose

`spi-altera-platform.c` is the platform-bus wrapper for the shared Altera SPI core. It handles platform data, OF matching, MMIO regmap setup, optional IRQ registration, and legacy board-info child creation.

## Important APIs, types, and functions

- `enum altera_spi_type` distinguishes normal MMIO controllers from `subdev_spi_altera` instances using a parent regmap and register offset.
- `spi_altera_config` describes the 32-bit MMIO regmap.
- `altera_spi_probe()` allocates and configures the SPI controller, maps or locates its regmap, initializes the shared core, requests an optional IRQ, registers the controller, and creates board-info devices from platform data.
- OF match table supports `ALTR,spi-1.0` and `altr,spi-1.0`.

## Control flow

Probe chooses host parameters from `struct altera_spi_platform_data` when present, otherwise defaults to 16 chipselects, `SPI_CS_HIGH`, and 1-16 bits per word. For subdevices it retrieves the parent regmap and optional register offset; for normal platform devices it maps MMIO and creates a regmap. It then calls `altera_spi_init_host()`, optionally requests `altera_spi_irq()`, registers the controller, and instantiates platform-data child devices.

## State and persistence behavior

State lives in the SPI controller and `struct altera_spi` private data. The wrapper uses non-devm `spi_alloc_host()` and calls `spi_controller_put()` on probe failure; successful registration is device-managed. Register state is initialized by the shared core and persists until transfers or device removal.

## Dependencies and integration points

The wrapper integrates with platform devices, device tree, legacy platform data, regmap-mmio, optional IRQs, and the exported Altera core. It consumes `struct altera_spi_platform_data` from `linux/spi/altera.h`.

## Risks and edge cases

- The IRQ is optional; missing or negative IRQs put the shared core into polling mode.
- Subdevice mode requires the parent to expose a regmap; otherwise probe fails.
- Platform-data device creation failures are warnings, not probe failures.
- Default chipselect and bits-per-word masks must match actual synthesized hardware when no platform data is supplied.

## Test signals

Build with `CONFIG_SPI_ALTERA`. Runtime tests should cover OF and platform-data probing, normal MMIO and subdevice regmap paths, IRQ and polling transfer modes, invalid `num_chipselect`, and child-device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-altera-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-amd-pci.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-amd-pci.c

## Purpose

`spi-amd-pci.c` is a PCI front-end for the AMD HID2 SPI controller. It discovers the SPI register window through an AMD LPC bridge PCI configuration register, maps the HID2 SPI aperture, sets version/bus metadata, and delegates registration to the shared AMD SPI implementation.

## Important APIs, types, and functions

- PCI ID table matches AMD vendor ID and LPC bridge device ID `0x1682`.
- `amd_spi_pci_probe()` allocates a SPI controller, reads config dword `0xA0`, masks the base address, adds `AMD_HID2_PCI_BAR_OFFSET`, maps `AMD_HID2_MEM_SIZE`, sets `AMD_HID2_SPI`, assigns bus number 2, and calls `amd_spi_probe_common()`.
- The module is registered with `module_pci_driver()`.

## Control flow

PCI core invokes probe for the LPC bridge. The probe path creates the controller and private `struct amd_spi`, maps the hardware, marks it as HID2, and reuses the common AMD SPI setup from `spi-amd.c`.

## State and persistence behavior

The front-end holds no independent mutable state after probe. Mapped IO and controller allocation are device-managed. Hardware state is managed by common AMD SPI code.

## Dependencies and integration points

The file depends on PCI, SPI framework, and `spi-amd.h`. It integrates with `amd_spi_probe_common()` exported by `spi-amd.c`, and is built together with it by `CONFIG_SPI_AMD`.

## Risks and edge cases

- The base address is read from PCI config rather than a normal BAR resource, so platform firmware correctness is critical.
- `devm_ioremap()` maps a physical address directly after masking and offsetting; there is no request-region protection in this wrapper.
- The bus number is fixed to 2, unlike the ACPI platform path using bus 0.

## Test signals

PCI enumeration on supported AMD hardware should show the `amd_spi_pci` driver binding, a mapped HID2 aperture, and successful controller registration. Build tests should ensure `spi-amd.o` exports `amd_spi_probe_common()` for this object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-amd-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-amd.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-amd.c

## Purpose

`spi-amd.c` implements the common AMD SPI master and SPI-MEM controller logic. It supports ACPI platform devices `AMDI0061`, `AMDI0062`, and `AMDI0063`, plus the PCI HID2 front-end through `amd_spi_probe_common()`.

The driver supports generic SPI messages through a FIFO/index command path and SPI-MEM operations for serial memories. HID2 adds DMA-style read/write support using a coherent 4 KiB-aligned buffer.

## Important APIs, types, and functions

- Register access helpers read/write 8/16/32/64-bit MMIO registers.
- `amd_spi_set_opcode()`, `amd_spi_set_rx_count()`, `amd_spi_set_tx_count()`, `amd_spi_busy_wait()`, and `amd_spi_execute_opcode()` abstract version-specific command execution.
- `amd_set_spi_freq()` chooses one of the hardware-supported speed encodings from `amd_spi_freq[]`.
- `amd_spi_fifo_xfer()` implements generic SPI message transfer through the FIFO, extracting the first TX byte as opcode.
- `amd_spi_supports_op()`, `amd_spi_adjust_op_size()`, and `amd_spi_exec_mem_op()` implement SPI-MEM validation and execution.
- `amd_spi_mem_data_in()`/`amd_spi_mem_data_out()` choose HID2 DMA paths for supported memory operations or fallback to index FIFO mode.
- `amd_spi_setup_hiddma()` allocates the coherent DMA buffer and programs HID2 interrupt/control registers.
- `amd_spi_probe_common()` fills the SPI controller fields and registers it; both the platform probe and PCI wrapper use it.

## Control flow

Platform probe maps MMIO from the platform resource, sets the version from ACPI match data, assigns bus 0, and calls common probe. The PCI wrapper maps HID2 registers separately and calls the same common path.

Generic SPI message flow selects the chip, walks `spi_message` transfers to collect opcode, TX data, RX length, and speed, writes FIFO/count registers, executes the opcode, waits for completion if RX is needed, reads FIFO data back, clears chip select on V2/HID2, and finalizes the message.

SPI-MEM flow checks opcode and size constraints, clamps operation size, sets per-op frequency, optionally toggles V2 4-byte address mode, then runs data-in or data-out. HID2 read/write commands use dedicated HID control registers and a coherent buffer; other paths use opcode/address/count/FIFO registers and busy polling.

## State and persistence behavior

`struct amd_spi` stores the MMIO base, current speed, hardware version, and HID2 DMA buffer address. Hardware state includes chip select, FIFO pointer, opcode/count registers, speed registers, V2 address mode, HID2 ring/output buffer registers, interrupt status, and control bits. Device-managed resources own controller registration and DMA allocation.

One subtle state issue: `amd_spi_probe_common()` registers the controller before calling `amd_spi_setup_hiddma()` for HID2. That means the controller can theoretically become visible before HID2 DMA setup succeeds.

## Dependencies and integration points

The driver depends on ACPI, platform devices, MMIO, DMA coherent allocation, SPI core, SPI-MEM, and the shared declarations in `spi-amd.h`. It exports `amd_spi_probe_common()` to the PCI wrapper.

## Risks and edge cases

- HID2 DMA helper functions poll interrupt status but ignore the return value from `readw_poll_timeout()`, so timeout failures may not propagate.
- The coherent DMA setup happens after `devm_spi_register_controller()`, which can leave a registered controller if HID2 setup fails.
- Generic FIFO transfer decrements `xfer->len` when consuming the opcode from the first TX transfer, mutating the transfer object.
- FIFO/index mode is capped at 64 data bytes, while the generic `max_transfer_size` reports 70 bytes including opcode/address overhead.
- HID2 read control computes `(op->data.nbytes / 4) - 1`; non-multiple-of-4 sizes need careful validation.
- Quad mode is limited to read operations by `supports_op()`, with write support limited to page-program opcodes.

## Test signals

Build with ACPI and PCI front-ends. Runtime tests should cover AMDI0061/0062/0063, generic SPI messages, SPI-MEM read/write/status operations, speed changes, V2 4-byte reads, HID2 4 KiB DMA reads and writes, non-4-byte-aligned lengths, chipselect handling for all four chipselects, and timeout injection for busy and HID2 interrupt polls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-amd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-amd.h -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-amd.h

## Purpose

`spi-amd.h` is the common private header for AMD SPI front-ends. It defines the hardware version enum, common private-data structure, and shared probe helper used by the platform and PCI wrappers.

## Important APIs, types, and functions

- `enum amd_spi_versions` distinguishes `AMD_SPI_V1`, `AMD_SPI_V2`, and `AMD_HID2_SPI`.
- `struct amd_spi` stores the remapped register base, HID2 DMA physical and virtual addresses, hardware version, and cached speed.
- `amd_spi_probe_common(struct device *dev, struct spi_controller *host)` is declared for front-ends to initialize and register a controller.

## Control flow

The header has no direct control flow. Front-end probes allocate a `spi_controller` with `sizeof(struct amd_spi)`, initialize version and MMIO address, then call `amd_spi_probe_common()`.

## State and persistence behavior

The structure fields persist for the lifetime of the SPI controller. `speed_hz` caches the selected hardware speed; `dma_virt_addr` and `phy_dma_buf` are only meaningful for HID2.

## Dependencies and integration points

The header depends on SPI controller types and DMA address types through included kernel headers in users. It is included by `spi-amd.c` and `spi-amd-pci.c`.

## Risks and edge cases

- Version values start at 1 and are used both as enum constants and ACPI match data; changing them would affect platform probe behavior.
- All front-ends must initialize `io_remap_addr` and `version` before calling the common probe.
- HID2 DMA fields must remain unused or NULL for non-HID2 versions.

## Test signals

Compile both AMD source files together and verify platform and PCI probes pass the expected `enum amd_spi_versions` values into the common code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-amd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-amlogic-spifc-a1.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-amlogic-spifc-a1.c

## Purpose

`spi-amlogic-spifc-a1.c` is a SPI-MEM-only driver for the Amlogic A1 SPI flash controller. It programs a user-command engine and a 512-byte data buffer to execute memory operations with single, dual, or quad bus widths.

## Important APIs, types, and functions

- `struct amlogic_spifc_a1` stores the SPI controller, clock, device, MMIO base, and cached current speed.
- `amlogic_spifc_a1_request()` starts a user request and polls for finish, plus data-updated for reads.
- `amlogic_spifc_a1_fill_buffer()` and `amlogic_spifc_a1_drain_buffer()` write/read the controller data buffer with 32-bit repeated IO and pad handling.
- `amlogic_spifc_a1_set_cmd()`, `set_addr()`, and `set_dummy()` program operation phases.
- `amlogic_spifc_a1_read()` and `write()` configure DIN/DOUT and trigger a request.
- `amlogic_spifc_a1_exec_op()` translates a `spi_mem_op` into command/address/dummy/data phases.
- `amlogic_spifc_a1_adjust_op_size()` clamps data transfers to `SPIFC_A1_BUFFER_SIZE`.
- PM callbacks disable/enable the clock and reinitialize hardware.

## Control flow

Probe maps MMIO, enables the controller clock, initializes hardware timing and AHB settings, enables runtime PM, configures the SPI controller for SPI-MEM with per-op frequency, and registers it.

For each SPI-MEM operation, the driver sets the requested clock rate, clears user registers, writes command/address/dummy configuration, resets the data-buffer pointer for data operations, then either reads, writes, or issues a no-data request. Reads wait for both finish and data-updated bits before draining the buffer.

## State and persistence behavior

The cached `curr_speed_hz` avoids redundant `clk_set_rate()` calls. Hardware state includes user control registers, data-buffer pointer, AHB enable state, timing register, and the clock rate. Runtime suspend disables the clock; resume calls `hw_init()` to restore baseline hardware state.

## Dependencies and integration points

The driver depends on OF platform probing (`amlogic,a1-spifc`), an unnamed clock, MMIO resources, runtime PM, and the SPI-MEM framework. It supports one chip select and 8-bit words with dual/quad TX/RX mode bits.

## Risks and edge cases

- The driver does not define a `supports_op()` callback; it relies on SPI-MEM defaults plus hardware errors and size adjustment.
- Dummy cycles are computed as `dummy.nbytes << 3` and do not divide by dummy bus width.
- `ilog2(buswidth)` assumes bus widths are powers of two; invalid widths should be filtered by the SPI-MEM framework.
- Buffer size is limited to 512 bytes, so large memory operations are split by the core.
- Runtime PM must keep the clock enabled during transfers through `auto_runtime_pm`.

## Test signals

Build with `CONFIG_SPI_AMLOGIC_SPIFC_A1`. Runtime tests should cover read ID/status, small and 512-byte reads/writes, split larger SPI-MEM operations, dual/quad modes, dummy cycles, per-op clock changes, runtime suspend/resume, and system sleep resume preserving hardware initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-amlogic-spifc-a1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-amlogic-spifc-a4.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-amlogic-spifc-a4.c

## Purpose

`spi-amlogic-spifc-a4.c` is a SPI-MEM flash-controller driver for Amlogic A4-class hardware. It supports raw SPI flash transfers and integrates a pipelined on-host NAND ECC engine for SPI NAND page read/write operations.

The controller uses a command FIFO, DMA-address commands, raw transfer-size fields, bus-width configuration, and an info buffer for ECC metadata/OOB bytes.

## Important APIs, types, and functions

- `struct aml_sfc` stores clocks, SPI controller, regmap, capability data, ECC engine, DMA addresses, scratch buffers, transfer flags, RX tuning, and chip-select state.
- `struct aml_sfc_ecc_cfg` and `struct aml_sfc_caps` describe supported BCH ECC layouts.
- `aml_sfc_wait_cmd_finish()`, `pre_transfer()`, and `end_transfer()` manage command FIFO sequencing and chip-select idle cycles.
- `aml_sfc_send_cmd()`, `send_addr()`, and `send_cmd_addr_dummy()` emit SPI-MEM command phases.
- `aml_sfc_dma_buffer_setup()` and `release()` map data and info buffers and program DMA address commands.
- `aml_sfc_raw_io_op()` handles non-ECC raw data transfers.
- `aml_sfc_read_page_hwecc()` and `write_page_hwecc()` use hardware BCH ECC, data/info scratch buffers, and OOB packing/unpacking.
- `aml_sfc_ecc_*` callbacks implement NAND on-host hardware ECC engine operations.
- `aml_sfc_setup()` applies SPI mode and clock settings.

## Control flow

Probe allocates a SPI controller, reads match data, maps the register block through regmap, allocates a combined data/info buffer, enables clocks, enables SPI mode, sets a 32-bit DMA mask, registers a NAND ECC engine, reads optional `amlogic,rx-adj`, fills controller callbacks/capabilities, and registers the SPI controller.

`exec_op()` selects chip select, emits pre-transfer idle/setup cycles, writes command/address/dummy phases, configures data bus width, then chooses the hardware-ECC page path for recognized SPI NAND page-cache opcodes when ECC is active and not raw. Otherwise it uses raw DMA transfer. ECC prepare/finish callbacks set transfer flags according to NAND page request mode and update MTD ECC stats after reads.

## State and persistence behavior

Hardware state persists in `SFC_SPI_CFG`, command FIFO, DMA address commands, clock rate, and CS selection. Software transfer flags in `sfc->flags` describe the current NAND page request mode (`DATA_ONLY`, `OOB_ONLY`, `DATA_OOB`, `AUTO_OOB`, `RAW_RW`, `HWECC`). ECC context is allocated per NAND device and stored both in `nand->ecc.ctx.priv` and `sfc->priv`. Scratch buffers are device-managed and reused across transfers.

## Dependencies and integration points

The driver depends on platform/OF (`amlogic,a4-spifc`), regmap-mmio, gate/core clocks, DMA mapping, SPI-MEM, MTD SPI NAND, and NAND ECC engine infrastructure. It advertises `mem_caps.ecc = true`, dual/quad/octal TX/RX mode bits, two chipselects, and min/max frequencies.

## Risks and edge cases

- The source contains duplicated lines in `aml_sfc_send_addr()` (`u8 val;`) and `aml_sfc_write_page_hwecc()` (`if (sfc->flags & SFC_AUTO_OOB)`), which would need cleanup in a compile-checked tree.
- `aml_sfc_wait_cmd_finish(sfc, 0)` in normal end-transfer converts to a zero timeout in regmap polling; behavior depends on polling helper semantics and may be too aggressive.
- DMA-safe buffer checks require 8-byte alignment and `virt_addr_valid()`; unaligned caller buffers are copied, adding allocation failure paths.
- ECC flag state is shared in `struct aml_sfc`; overlapping operations are expected to be serialized by the SPI/NAND stack.
- OOB layout assumes BCH8 info bytes and two user bytes per step.
- The hardware-ECC page path recognizes opcodes by command value and depends on NAND ECC prepare/finish sequencing to set data/OOB flags.

## Test signals

Build with SPI-MEM, MTD, and NAND ECC support. Runtime tests should cover raw SPI NOR-style reads/writes, SPI NAND page reads/writes with hardware ECC, raw NAND mode, OOB-only and data+OOB modes, ECC correction and uncorrectable errors, DMA buffer alignment fallbacks, dual/quad/octal opcode bus widths, clock clamping, and two chipselects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-amlogic-spifc-a4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-amlogic-spisg.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-amlogic-spisg.c

## Purpose

`spi-amlogic-spisg.c` is a generic SPI controller driver for the Amlogic A4 SPI scatter-gather communication controller. Unlike the SPIFC drivers, it implements normal SPI message transfer using DMA descriptors and supports host or target allocation depending on the `spi-slave` device-tree property.

## Important APIs, types, and functions

- `struct spisg_device` stores controller/device pointers, regmap, clocks, completion, status, cached speed, and cached config register values.
- `struct spisg_descriptor` is the hardware descriptor with start/bus config and TX/RX physical addresses.
- `struct spisg_descriptor_extra` tracks allocated TX/RX scatter-gather link tables for cleanup.
- `aml_spisg_clk_init()` creates a divider clock backed by the controller `CFG_CLK_DIV` field.
- `aml_spisg_setup_transfer()` translates a `spi_transfer` into a descriptor, maps linear or SG buffers, sets lane, op mode, data mode, block size/count, and speed.
- `aml_spisg_transfer_one_message()` allocates descriptor arrays, adds optional CS hold delay descriptor, maps descriptors, starts hardware, waits for IRQ completion, cleans DMA mappings, finalizes the SPI message, and releases the hardware semaphore.
- `aml_spisg_prepare_message()` derives CPOL/CPHA/LSB/3-wire/chipselect settings from the SPI device.
- `aml_spisg_irq()` handles descriptor error and chain-done interrupts.
- Runtime PM callbacks switch clocks and pinctrl state.

## Control flow

Probe chooses host or target controller allocation, maps registers, creates regmap, resets the device, initializes clocks and default config, enables runtime PM, fills SPI controller callbacks and limits, requests the IRQ, registers the controller, and releases the initial runtime PM reference.

Transfer flow starts by acquiring the controller semaphore register. It counts transfers, allocates descriptors plus extra tracking records, configures each transfer, calculates timeout from transfer length and effective speed, optionally appends a null descriptor for CS hold, marks the final descriptor EOC, maps the descriptor list, writes descriptor-list registers, waits for completion, unmaps all resources, updates `actual_length` on success, finalizes the message, and releases the semaphore.

## State and persistence behavior

Cached config state (`cfg_spi`, `cfg_start`, `cfg_bus`) is reused across descriptors and updated per message/transfer. Hardware semaphore state is stored in `SPISG_REG_CFG_READY`. Runtime PM turns `sclk` and `core` clocks on/off and selects pinctrl default/sleep states. DMA descriptor and SG-link allocations are per-message and freed after completion.

## Dependencies and integration points

The driver depends on OF (`amlogic,a4-spisg`), regmap-mmio, reset control, clocks (`core`, `pclk`, generated divider `sclk`), DMA mapping, IRQs, pinctrl PM states, runtime PM, and the SPI core. It advertises quad TX/RX, 3-wire, CPOL/CPHA, LSB-first, DMA capability, and target abort.

## Risks and edge cases

- The source contains duplicated `if (!paddr) {` and `if (ret) {` lines in `aml_spisg_setup_transfer()`/`clk_init()` as read here; this must be resolved in compile-tested code.
- `can_dma()` unconditionally returns true, so DMA mapping paths must handle all transfer buffers correctly.
- `nbits_to_lane[xfer->tx_nbits]` and RX equivalent assume valid nbits indexes within 0..4.
- Descriptor allocation packs `struct spisg_descriptor` and `struct spisg_descriptor_extra` in one allocation with manual pointer arithmetic; size/count changes need care.
- Error paths after partial descriptor setup must clean only mappings that were established; descriptor fields are zeroed to help.
- Timeout is estimated from data length and speed with tolerance, but target mode can wait indefinitely.
- Remove disables `core` and `pclk`, while runtime suspend disables `sclk` and `core`; clock-state symmetry should be tested.

## Test signals

Build with `CONFIG_SPI_AMLOGIC_SPISG`. Runtime tests should cover PIO-sized and large DMA messages, TX-only/RX-only/full-duplex-looking half-duplex transfers, SG and linear buffers, quad lane transfers, CS setup/hold delays, target mode and target abort, runtime suspend/resume, IRQ error bits, descriptor-chain completion, and semaphore-busy handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-amlogic-spisg.c -->
