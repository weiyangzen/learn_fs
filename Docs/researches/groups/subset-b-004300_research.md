# Research: subset-b-004300 SPI NOR core files

Work item: `subset-b-004300`

This grouped report covers the SPI NOR core, SFDP parser, debugfs, OTP, and selected manufacturer tables under `sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/`. Each section is bounded with the required reconciliation markers for splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/core.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/core.c

## Purpose

`core.c` is the central Linux MTD SPI NOR framework implementation. It binds as a `spi_mem_driver`, detects or matches a flash device, derives `spi_nor_flash_parameter` data from defaults, manufacturer fixups, SFDP, and late fixups, negotiates supported read/program/erase protocols with the controller, registers an `mtd_info`, and implements the MTD read, write, erase, suspend, resume, remove, and shutdown paths. It also exports `spi_nor_scan()` for controller-specific users.

## Important APIs, types, and functions

The main public entry point is `spi_nor_scan()`, exported with `EXPORT_SYMBOL_GPL`, which validates `struct spi_nor`, allocates a bounce buffer, hardware-resets the part when a reset GPIO exists, resolves `flash_info`, initializes parameters, selects controller-compatible operations, initializes the chip, and fills MTD callbacks.

Key helper families include register access (`spi_nor_read_id`, `spi_nor_read_sr`, `spi_nor_read_cr`, `spi_nor_write_sr`, `spi_nor_write_sr_and_check`), write-enable and readiness (`spi_nor_write_enable`, `spi_nor_write_disable`, `spi_nor_wait_till_ready`), protocol helpers (`spi_nor_spimem_setup_op`, `spi_nor_read_data`, `spi_nor_write_data`, `spi_nor_read_any_reg`, `spi_nor_write_any_volatile_reg`), quad/4-byte/octal mode setup, erase map execution, and MTD operation callbacks.

`manufacturers[]` integrates manufacturer modules by referencing `spi_nor_eon`, `spi_nor_esmt`, `spi_nor_everspin`, `spi_nor_gigadevice`, `spi_nor_intel`, `spi_nor_issi`, `spi_nor_macronix`, `spi_nor_micron`, `spi_nor_st`, and others outside this group.

## Control flow

Probe begins in `spi_nor_probe()`: it enables the `vcc` regulator, allocates and initializes `struct spi_nor`, chooses a flash name from platform data or modalias, calls `spi_nor_scan()`, registers debugfs, creates read/write direct maps, and finally calls `mtd_device_register()`.

`spi_nor_scan()` resets protocols to 1-1-1, allocates an early bounce buffer, optionally toggles hardware reset, detects or matches flash info, initializes `nor->params`, optionally initializes RWW wait queues, calls `spi_nor_setup()` to select the actual read/program/erase path, runs `spi_nor_init()` to enter octal/quad/4-byte modes and optional unlock-all behavior, and installs MTD callbacks.

Read/write/erase MTD flows wrap controller preparation and locking. Reads call `spi_nor_prep_and_lock_rd()` and loop through `spi_nor_read_data()` or the octal-DTR alignment helper. Writes split by page boundaries, issue WREN, program one page fragment, wait ready, and advance `retlen`. Erases choose chip/die erase, uniform sector erase, or non-uniform erase-command lists built from the erase map.

## State and persistence behavior

Persistent device state includes volatile and non-volatile flash modes and registers: quad enable bits, 4-byte address mode, status/configuration registers, software protection bits, octal-DTR mode bits, and erase/program effects on the flash array. Driver state is held in `struct spi_nor`: opcodes, protocols, address byte count, `params`, cached JEDEC ID, cached SFDP pointer, bounce buffer, direct-map descriptors, `mtd_info`, flags, and RWW lock state.

Shutdown and remove call `spi_nor_restore()` to exit 4-byte mode when needed and issue a soft reset if SFDP advertised reset support. Suspend disables volatile octal-DTR mode; resume calls `spi_nor_init()` again.

## Dependencies and integration points

The file depends on Linux MTD, SPI, SPI-mem, GPIO descriptor reset, regulator, OF properties (`broken-flash-reset`, `no-wp`, `m25p,fast-read`), debugfs/sysfs hooks, SFDP parsing, OTP and locking helpers, and manufacturer `flash_info` tables. It supports both modern `spi_mem` paths and legacy `controller_ops`, with DTR register operations rejected for legacy controller ops.

## Risks

Capability selection is safety-critical: wrong SFDP parsing or fixups can select unsupported opcodes, bus widths, dummy cycles, address widths, or erase sizes. Stateful mode transitions are especially risky on systems with broken reset lines because a crash can leave flash in 4-byte or octal-DTR mode for boot firmware. RWW locking is complex and bank-based; mistakes can allow reads during program/erase of the same bank or over-serialize otherwise safe access. Octal-DTR odd-address alignment uses temporary buffers and 0xff padding, so partial transfer accounting must remain exact. Non-uniform erase planning must avoid erasing outside requested ranges, especially for overlaid regions.

## Test signals

Useful tests include JEDEC/SFDP probe on known parts, spi-mem operation support filtering, MTD read/write/erase with unaligned and page-boundary ranges, large erase ranges across uniform and non-uniform maps, suspend/resume and remove/shutdown restoration, RWW concurrent read/program tests on multi-bank parts, debugfs parameter inspection, and boot-cycle tests for `broken-flash-reset` platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/core.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/core.h

## Purpose

`core.h` is the internal contract for the SPI NOR subsystem. It defines standard SPI memory operation templates, internal flags, command descriptors, erase-map structures, OTP structures, flash identification records, manufacturer registration objects, SFDP cache structures, and prototypes shared by the core, SFDP, OTP, locking, debugfs, and manufacturer files.

## Important APIs, types, and functions

The header defines `SPI_NOR_*_OP` macros for read ID, write enable/disable, status/configuration register access, 4-byte mode entry/exit, bank register write, global block unlock, die/sector erase, read, page program, and software reset. These macros produce `struct spi_mem_op` templates consumed by `core.c`, `sfdp.c`, `otp.c`, and manufacturer octal-DTR code.

Key types include `spi_nor_flash_parameter`, `spi_nor_fixups`, `flash_info`, `spi_nor_manufacturer`, `spi_nor_erase_map`, `spi_nor_erase_region`, `spi_nor_erase_type`, `spi_nor_otp_organization`, and `spi_nor_otp_ops`. The `SNOR_ID()` and `SNOR_OTP()` macros create inline static descriptors for manufacturer tables.

The prototype list exposes the internal helper surface: register I/O, data I/O, write-enable, readiness, quad-enable methods, 4-byte mode methods, erase helpers, OTP helpers, SFDP parser entry points, locking and OTP MTD setup, and debugfs registration.

## Control flow

`core.h` does not execute runtime control flow, but it shapes the runtime pipeline. `flash_info` entries feed `spi_nor_get_flash_info()` and `spi_nor_init_params()`. `spi_nor_fixups` hooks are invoked in default, BFPT, SMPT, post-SFDP, and late phases. `spi_nor_flash_parameter` becomes the state object consumed by setup, MTD callbacks, debugfs, and manufacturer fixups.

## State and persistence behavior

The header distinguishes transient driver flags (`SNOR_F_*`) from flash capabilities and flash-specific metadata (`SPI_NOR_*` flags in `flash_info`). Some flags represent persistent or semi-persistent hardware state, such as software protection volatility, 4-byte opcode support, volatile I/O mode enable, soft reset support, ECC behavior, and RWW support.

OTP metadata records physical OTP layout but does not itself persist data; persistence is implemented by the flash and surfaced through `otp.c`.

## Dependencies and integration points

It includes `sfdp.h` and depends on public SPI NOR, MTD, SPI-mem, list, and kernel bit macros through the included translation units. Manufacturer modules export `const struct spi_nor_manufacturer` objects declared here, while the core consumes them through `manufacturers[]`.

## Risks

This header is a high-blast-radius ABI inside the driver. Any mismatch between `SNOR_F_*` names and `debugfs.c` display tables produces bad diagnostics. Incorrect `SPI_MEM_OP` templates can corrupt operation direction, bus width, or address length across all users. In particular, register op templates should be reviewed carefully because their direction fields directly determine how spi-mem controllers perform transactions. Flag overloading can also lead to confusion: `flash_info.flags`, `no_sfdp_flags`, `fixup_flags`, and runtime `nor->flags` have different meanings.

## Test signals

Build coverage should include all SPI NOR translation units. Runtime validation should check debugfs flag names, SFDP and non-SFDP probes, OTP user-prot registration, quad-enable methods, 4-byte mode selection, and manufacturer fixup paths that call these prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/debugfs.c

## Purpose

`debugfs.c` exposes runtime SPI NOR configuration through debugfs. It creates a global `spi-nor` root and per-device directories containing `params` and `capabilities` files. These files let developers inspect detected flash identity, selected opcodes, protocols, flags, erase commands, sector map, and supported read/program modes.

## Important APIs, types, and functions

`spi_nor_debugfs_register()` creates the per-device directory and files. `spi_nor_debugfs_shutdown()` removes the root directory at module exit. `spi_nor_debugfs_unregister()` is registered as a devm action to remove a device directory on detach.

`spi_nor_params_show()` prints selected live state from `struct spi_nor` and `struct spi_nor_flash_parameter`. `spi_nor_capabilities_show()` walks `params->hwcaps.mask`, converts each bit to read/program command indexes through `spi_nor_hwcaps_read2cmd()` and `spi_nor_hwcaps_pp2cmd()`, and prints command details.

## Control flow

The core calls `spi_nor_debugfs_register(nor)` after a successful scan in `spi_nor_probe()`. On first registration, the file creates the root directory. It then registers a devm cleanup callback, creates a device-named subdirectory, and creates read-only seq files. The seq show functions run when users read the debugfs files and access live driver state.

## State and persistence behavior

The file does not persist state. It exposes current in-memory state, including opcodes/protocols that may have been changed by SFDP parsing, fixups, controller capability filtering, and octal-DTR setup. The static `rootdir` pointer tracks global debugfs root lifetime.

## Dependencies and integration points

It depends on debugfs, seq_file show helpers, SPI NOR internals from `core.h`, public SPI NOR protocol enums, and SPI/SPI-mem types. The `snor_f_names[]` array must remain in sync with `enum spi_nor_option_flags` in `core.h`.

## Risks

The file is diagnostic, not data-path critical, but stale or incorrect output can mislead debugging of flash bring-up. `rootdir` creation is lazy and global; cleanup relies on module exit and devm per-device removal. If flag names fall out of sync, debugfs will show wrong flags. Reading live state assumes the device remains valid through debugfs lifetime, which is mitigated by devm removal.

## Test signals

Mount debugfs and verify `/sys/kernel/debug/spi-nor/<device>/params` and `capabilities` after probing several devices. Check that selected opcodes, protocols, erase map, and flags match SFDP dumps and expected manufacturer fixups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/eon.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/eon.c

## Purpose

`eon.c` registers Eon SPI NOR parts with the core framework. It is a manufacturer table only: it lists JEDEC IDs, legacy names, sizes, and non-SFDP capability hints for EN25 devices.

## Important APIs, types, and functions

The file defines `eon_nor_parts[]` and exports `const struct spi_nor_manufacturer spi_nor_eon`. Entries use `SNOR_ID()` and `flash_info` fields such as `.name`, `.size`, and `.no_sfdp_flags`.

## Control flow

The core's `manufacturers[]` includes `spi_nor_eon`. During detection, `spi_nor_match_id()` compares read JEDEC bytes against `eon_nor_parts[]`. If matched, the selected entry feeds default and non-SFDP parameter initialization.

## State and persistence behavior

The file has no mutable state. It contributes static probe metadata. For legacy parts with `.size` set, the core may avoid mandatory SFDP parsing and use `.no_sfdp_flags` to initialize 4K erase and dual-read support.

## Dependencies and integration points

It depends on public `linux/mtd/spi-nor.h` constants and internal `core.h`. It integrates only through the `spi_nor_eon` manufacturer object.

## Risks

Incorrect ID or size entries cause wrong MTD size or wrong device binding. Missing `SECT_4K` or read-mode hints can reduce functionality on parts without usable SFDP; over-declaring dual-read can select operations unsupported by old devices.

## Test signals

Probe known EN25 parts, compare MTD size and erase size with datasheets, verify JEDEC matching for entries with IDs, and run read/erase/write tests on devices using `SECT_4K` or dual-read hints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/eon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/esmt.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/esmt.c

## Purpose

`esmt.c` registers ESMT F25L/F25Q SPI NOR parts. It provides static `flash_info` entries for a small set of devices, including software protection capabilities.

## Important APIs, types, and functions

The file defines `esmt_nor_parts[]` and exports `spi_nor_esmt`. Entries identify devices with `SNOR_ID()`, set `.size`, set `SECT_4K`, and mark lock support with `SPI_NOR_HAS_LOCK`; `f25l32pa` also uses `SPI_NOR_SWP_IS_VOLATILE`.

## Control flow

The core matches JEDEC IDs to this manufacturer table. Runtime behavior then follows common core paths: `spi_nor_init_flags()` converts table flags into runtime lock and volatile-protection flags, `spi_nor_init_default_locking_ops()` can be selected during late init, and non-SFDP flags seed erase settings.

## State and persistence behavior

No local mutable state exists. The table affects persistent flash protection behavior by telling the core that block protection bits exist and may be volatile after power-on.

## Dependencies and integration points

It depends on `core.h` definitions and integrates with the generic lock setup in the SPI NOR core and locking helper files.

## Risks

Protection flags have direct user-visible effects. If `SPI_NOR_HAS_LOCK` or `SPI_NOR_SWP_IS_VOLATILE` is wrong, the core may expose invalid lock operations or unlock a device unexpectedly under `CONFIG_MTD_SPI_NOR_SWP_DISABLE*`. Size or erase hints must match hardware.

## Test signals

Probe each ESMT ID, verify `mtd->_lock/_unlock/_is_locked` behavior where exposed, confirm volatile protection behavior after reset, and run erase/write tests with 4K sector alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/esmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/everspin.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/everspin.c

## Purpose

`everspin.c` adds Everspin MRAM/FRAM-like SPI parts to the SPI NOR framework. These devices are non-erase memories, so the table and fixup adapt the NOR core to operate without erase and without fast-read support.

## Important APIs, types, and functions

`everspin_nor_parts[]` lists `mr25h128`, `mr25h256`, `mr25h10`, and `mr25h40` with sizes, sector sizes, two-byte addressing for the smaller parts, and `SPI_NOR_NO_ERASE`. `everspin_nor_default_init()` clears `SNOR_HWCAPS_READ_FAST`, and `everspin_nor_fixups` wires that hook into the exported `spi_nor_everspin` manufacturer.

## Control flow

These parts are typically matched by modalias/name rather than JEDEC ID. During parameter initialization, the manufacturer default fixup removes fast read before capability selection. Later, `spi_nor_set_mtd_info()` sees `SPI_NOR_NO_ERASE`, sets `MTD_NO_ERASE`, and does not install `_erase`.

## State and persistence behavior

No local mutable state exists. The file changes runtime behavior so writes are treated like direct programming of non-erase memory and no erase persistence model is exposed.

## Dependencies and integration points

It depends on the core's name matching, default fixup hook, MTD `MTD_NO_ERASE` handling, and static SPI device IDs in `core.c` for Everspin names.

## Risks

Treating MRAM as NOR-compatible is intentionally special. If an Everspin part actually requires different write semantics, the generic page-program path may be wrong. Removing fast read is important because the devices do not support the opcode; missing this would break reads after setup.

## Test signals

Bind by each supported name, confirm MTD has `MTD_NO_ERASE`, perform read/write without erase, verify two-byte addressing on 16K/32K parts, and confirm selected read opcode is normal read rather than fast read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/everspin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/gigadevice.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/gigadevice.c

## Purpose

`gigadevice.c` registers GigaDevice GD25Q/GD25LQ SPI NOR parts and provides a targeted SFDP fixup for `gd25q256`.

## Important APIs, types, and functions

`gd25q256_post_bfpt()` inspects BFPT version. For first-generation JESD216 data on GD25Q256C, it overrides `params->quad_enable` to `spi_nor_sr1_bit6_quad_enable()` because early SFDP does not define Quad Enable requirements. `gd25q256_fixups` attaches that hook.

`gigadevice_nor_parts[]` lists supported JEDEC IDs, sizes for non-SFDP parts, lock/top-bottom flags, 4K sector and dual/quad read hints, and `SPI_NOR_4B_OPCODES` for `gd25q256`.

## Control flow

The core detects a GigaDevice ID, applies default parameter setup, parses SFDP when required, calls the part `post_bfpt` fixup for `gd25q256`, and later converts flash flags into runtime lock and addressing behavior.

## State and persistence behavior

No local mutable state exists. Table flags influence persistent protection handling. The quad-enable fixup writes status register bit 6 at runtime when quad I/O is selected.

## Dependencies and integration points

The file depends on `sfdp.h` BFPT revision constants through `core.h`, quad-enable helpers from `core.c`, and common lock/addressing setup.

## Risks

The GD25Q256 ID spans multiple generations with different SFDP quality. The fixup must be narrowly version-gated so newer parts keep their SFDP-defined behavior. Incorrect lock/top-bottom flags can expose wrong protection ranges. Missing 4-byte opcode handling can break accesses above 16 MiB.

## Test signals

Probe GD25Q16/32/64/128 and GD25Q256 generations, verify debugfs quad-enable method effects, test lock/unlock regions, run reads and writes above 16 MiB on GD25Q256, and compare selected capabilities against SFDP dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/gigadevice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/intel.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/intel.c

## Purpose

`intel.c` registers a small set of Intel S33B SPI NOR parts. The table is focused on device identity, size, lock support, and volatile software protection.

## Important APIs, types, and functions

The file defines `intel_nor_parts[]` for `160s33b`, `320s33b`, and `640s33b`, then exports `spi_nor_intel`. Each entry uses JEDEC-like IDs, sets size, and sets `SPI_NOR_HAS_LOCK | SPI_NOR_SWP_IS_VOLATILE`.

## Control flow

The common detection path matches IDs through `spi_nor_match_id()`. During late init, `spi_nor_init_flags()` turns table flags into runtime lock and volatile-protection flags, and the core may install default locking operations.

## State and persistence behavior

No local mutable state exists. The table tells the core that software protection bits exist and are volatile, affecting unlock-at-init behavior depending on kernel configuration.

## Dependencies and integration points

It integrates with the generic SPI NOR manufacturer registry, lock support, and MTD protection callbacks. It has no custom fixups.

## Risks

The main risk is protection semantics. Wrong volatile-protection flags can cause unexpected unlock or missing unlock after reset. There are no `no_sfdp_flags`, so behavior depends on defaults and/or SFDP availability for more advanced parameters.

## Test signals

Probe all listed parts, verify MTD size, confirm lock/unlock/is_locked behavior, and test power-cycle protection defaults with relevant `CONFIG_MTD_SPI_NOR_SWP_DISABLE*` settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/intel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/issi.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/issi.c

## Purpose

`issi.c` registers ISSI and PMC SPI NOR parts and provides fixups for address-width and erase-opcode quirks.

## Important APIs, types, and functions

`is25lp256_post_bfpt_fixups()` corrects BFPT data that advertises 3-byte-only addressing despite 4-byte opcode support by setting `params->addr_nbytes = 4`. `pm25lv_nor_late_init()` changes 4K erase opcodes to `SPINOR_OP_BE_4K_PMC` for PM25LV devices. `issi_nor_default_init()` sets the manufacturer default quad-enable method to `spi_nor_sr1_bit6_quad_enable()`.

The table covers PM25LV, IS25CD, PM25LQ, IS25LQ/LP/WP devices with IDs, sizes, 4K sector hints, dual/quad read hints, quad page program support, and 4-byte opcode fixup flags.

## Control flow

During probe, matching entries feed common parameter setup. Manufacturer default init sets quad enable early. BFPT parsing may invoke the IS25LP256 fixup. Late init may rewrite PM25LV erase opcodes after the erase map exists. Setup then selects read/program/erase operations from the corrected parameters.

## State and persistence behavior

No local mutable state exists. The fixups influence runtime parameter state and may cause status-register writes for quad enable. PM25LV erase opcode correction affects persistent erase behavior on those parts.

## Dependencies and integration points

The file depends on SFDP BFPT macros, core erase-map structures, quad-enable helpers, and the generic fixup hook sequence.

## Risks

Address-width correction is critical for 256 Mbit parts; if wrong, accesses above 16 MiB fail or wrap. The PM25LV 4K opcode quirk must only apply to PM25LV entries. Manufacturer-wide quad-enable defaults could be wrong for a future ISSI part unless overridden by SFDP or part fixups.

## Test signals

Test PM25LV 4K erase, IS25LP256/IS25WP256 reads above 16 MiB, quad-read enable on LP/WP devices, and compare debugfs erase command lists before and after late init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/issi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/macronix.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/macronix.c

## Purpose

`macronix.c` registers Macronix SPI NOR parts and implements Macronix-specific fixups for quad page program, quad enable, 4-byte address mode defaults, and octal-DTR mode transitions.

## Important APIs, types, and functions

`mx25l25635_post_bfpt_fixups()` distinguishes ID-reused MX25L25635 variants by checking BFPT 4-4-4 fast read support and sets `SNOR_F_4B_OPCODES` for the newer variant. `macronix_qpp4b_post_sfdp_fixups()` adds missing 1-1-4 page program support with a 4-byte opcode. `mx25l3255e_late_init_fixups()` supplies missing quad-enable and 1-4-4 page program settings for older SFDP.

The octal-DTR helpers write CR2 dummy-cycle and mode registers, verify mode switches by reading JEDEC ID, and support both enable and disable paths. Manufacturer late init supplies default 4-byte mode entry and `set_octal_dtr`.

## Control flow

After matching a Macronix part, the core applies manufacturer default init, SFDP parsing, part post-BFPT/post-SFDP fixups, manufacturer late init, and then capability selection. If the selected read/write protocols are 8D-8D-8D and the volatile I/O-mode flag is set, `spi_nor_set_octal_dtr()` calls the Macronix mode switch helper.

## State and persistence behavior

Static tables have no mutable state, but mode helpers write volatile CR2 registers on the flash. The driver verifies transitions by reading IDs in the expected protocol. Shutdown and suspend can disable volatile octal mode through the core. Quad enable may persist depending on part register behavior.

## Dependencies and integration points

The file uses `spi_nor_write_any_volatile_reg()`, `spi_nor_read_id()`, `spi_nor_set_pp_settings()`, `spi_nor_set_4byte_addr_mode_en4b_ex4b()`, and SFDP BFPT macros. It integrates heavily with core mode setup and SFDP fixup hooks.

## Risks

Macronix has ID reuse and incomplete SFDP on several parts, so fixup scope matters. Octal-DTR mode switching is stateful; failed disable can leave the device inaccessible to boot firmware. Dummy-cycle conversion through `MXIC_NOR_REG_DC()` must match hardware encoding. ID verification assumes duplicated bytes in 8D reads, so controller byte ordering and `SNOR_F_SWAP16` interactions need coverage.

## Test signals

Test MX25L25635E/F differentiation, MX25L3255E quad and 1-4-4 page program, 4-byte reads/writes/erases on large parts, octal-DTR entry/exit on MX25UW51245G, suspend/resume restoration, and debugfs protocol/opcode output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/macronix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/micron-st.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/micron-st.c

## Purpose

`micron-st.c` registers Micron and ST SPI NOR parts and implements shared Micron/ST behavior: flag-status-register readiness, octal-DTR entry/exit, multi-die erase setup, and several part-specific SFDP fixups.

## Important APIs, types, and functions

The file defines Micron opcodes and FSR bits, `micron_st_nor_octal_dtr_en/dis()`, `micron_st_nor_ready()`, multi-die late init helpers, `mt35xu512aba_post_sfdp_fixup()`, `mt25qu512a_post_bfpt_fixup()`, and exported manufacturers `spi_nor_micron` and `spi_nor_st`.

`micron_st_nor_ready()` combines normal status-register readiness with FSR reads, reports erase/program/protection errors, clears FSR, and sends write-disable on program/erase errors to avoid accidental later writes.

## Control flow

Probe matches Micron or ST entries, applies manufacturer default init to set lock support, clear 16-bit status default, and disable quad enable. SFDP and part fixups add octal-DTR settings, multi-die metadata, or status quirks. Late init installs FSR readiness for entries with `USE_FSR`, defaults 4-byte mode to WREN+EN4B/EX4B when absent, and installs octal-DTR switching.

## State and persistence behavior

The file writes volatile configuration registers to enter/exit octal-DTR mode. Multi-die late init sets die erase opcode and `n_dice`, and enters 4-byte address mode so die erase can work. FSR error bits are cleared after detection. Protection state and data persistence remain in flash hardware.

## Dependencies and integration points

It depends on core register and spi-mem helpers, `spi_nor_set_read_settings()`, `spi_nor_set_pp_settings()`, 4-byte address helpers, and readiness polling in `core.c`. The ST and Micron tables share the same manufacturer fixups.

## Risks

FSR handling changes error reporting and write-latch cleanup; if unsupported by a controller, fallback to status-only readiness is intentional only for `-EOPNOTSUPP`. Octal-DTR mode writes must be reversible or shutdown/resume can leave the flash in an unexpected protocol. Multi-die late init enters 4-byte mode during parameter initialization, which is persistent until restored and can affect boot safety. Large legacy tables have many IDs where size, lock flags, and FSR flags must remain exact.

## Test signals

Run program/erase failure injection or protected-sector tests to verify FSR error handling and write-disable. Test octal-DTR read/write on MT35XU parts, multi-die chip erase on N25Q/MT25Q large parts, 4-byte access above 16 MiB, suspend/resume, and controller paths that do not support RDFSR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/micron-st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/otp.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/otp.c

## Purpose

`otp.c` implements user OTP support for SPI NOR flashes. It maps vendor security-register operations into the MTD user protection register API, handles contiguous logical OTP offsets, enforces region alignment for erase/lock, checks lock status before destructive operations, and installs MTD OTP callbacks when a flash supplies OTP ops.

## Important APIs, types, and functions

Generic security-register helpers are `spi_nor_otp_read_secr()`, `spi_nor_otp_write_secr()`, `spi_nor_otp_erase_secr()`, `spi_nor_otp_lock_sr2()`, and `spi_nor_otp_is_locked_sr2()`. These are used by flash entries that represent OTP as Winbond/GigaDevice-style security registers.

MTD callbacks include `spi_nor_mtd_otp_info()`, `spi_nor_mtd_otp_read()`, `spi_nor_mtd_otp_write()`, `spi_nor_mtd_otp_erase()`, and `spi_nor_mtd_otp_lock()`. `spi_nor_set_mtd_otp_ops()` installs those callbacks on `mtd_info`.

## Control flow

The core calls `spi_nor_set_mtd_otp_ops()` while filling MTD info. If `params->otp.ops` is absent, nothing is exposed. Reads and writes validate/logically clamp offsets, lock the device, translate logical MTD offsets into physical OTP region addresses, and call the supplied OTP ops one region at a time. Writes first check whether any affected region is locked. Erase and lock require whole-region aligned ranges.

## State and persistence behavior

OTP data, erase state, and lock bits persist in flash hardware. The code temporarily overrides `nor->read_opcode`, `program_opcode`, protocols, address bytes, and direct-map descriptors to issue security-register commands, then restores previous state. Locking uses status/configuration register bits via SR2/CR helpers.

## Dependencies and integration points

It depends on `core.h` SPI NOR helpers, MTD OTP callback contracts, `spi_nor_prep_and_lock()`, write-enable and readiness helpers, and flash-supplied `spi_nor_otp_ops`/organization metadata.

## Risks

Temporary mutation of `struct spi_nor` opcodes and direct-map descriptors must always be restored on error. OTP writes are one-way on many devices, and lock operations are irreversible, so range validation and lock checks are critical. Logical-to-physical offset translation assumes region length is a power of two; `spi_nor_set_mtd_otp_ops()` warns and refuses otherwise. Reads and writes must not span unsupported physical security registers except through the per-region loop.

## Test signals

Test `_get_user_prot_info`, read/write, lock, and erase on a flash with OTP ops. Verify locked writes and erases return `-EROFS`, partial logical reads across regions split correctly, unaligned erase/lock returns `-EINVAL`, and normal flash read/write opcodes still work after OTP errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/otp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sfdp.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sfdp.c

## Purpose

`sfdp.c` parses JEDEC Serial Flash Discoverable Parameters and turns flash-resident tables into SPI NOR runtime parameters. It discovers density, address width, read modes, erase types, page size, quad-enable requirements, 4-byte opcode support, non-uniform sector maps, xSPI Profile 1.0 octal-DTR settings, SCCR volatile register offsets, and soft-reset or byte-order flags.

## Important APIs, types, and functions

Public entry points are `spi_nor_check_sfdp_signature()` and `spi_nor_parse_sfdp()`. Internal parser stages include `spi_nor_parse_bfpt()`, `spi_nor_parse_smpt()`, `spi_nor_parse_4bait()`, `spi_nor_parse_profile1()`, `spi_nor_parse_sccr()`, `spi_nor_parse_sccr_mc()`, and post-SFDP fixup dispatch.

Important helpers include `spi_nor_read_sfdp()`, which temporarily forces the RDSFDP opcode, 3-byte address, and 8 dummy cycles; erase-type sorting and mask translation helpers; SMPT map-selection helpers that run detection commands; and 4BAIT conversion code that updates read/program/erase opcodes to 4-byte variants.

## Control flow

`spi_nor_parse_sfdp()` reads and validates the SFDP header, reads optional parameter headers once, caches a bounded complete SFDP dump in `nor->sfdp`, chooses the newest BFPT header, parses BFPT, then iterates optional tables. Optional parser failures are warned but do not discard already-parsed base parameters. Finally it runs manufacturer and part post-SFDP fixups.

BFPT parsing sets density, address bytes, fast-read capabilities, erase types, page size, quad-enable method, 4-byte mode method, soft-reset support, octal read instructions, command extension type, and 8D byte swap flag. SMPT can replace uniform erase maps with non-uniform regions. 4BAIT can force 4-byte opcodes. Profile 1 adds 8D-8D-8D read/program support and status-register dummy/address requirements.

## State and persistence behavior

The parser mainly mutates in-memory `nor->params` and `nor->flags`. It also temporarily mutates read opcode/address/dummy fields while reading SFDP or SMPT detection bytes, restoring them before return. The cached `nor->sfdp` is devm-managed for later sysfs/debug access.

## Dependencies and integration points

It depends on `core.h`, `sfdp.h`, bitfield helpers, sort, kmalloc/devm allocation, SPI NOR data I/O helpers, and manufacturer fixup hooks. Its outputs are consumed by core setup, debugfs, sysfs, manufacturer octal-DTR code, erase planning, and MTD geometry.

## Risks

SFDP is untrusted device data. Bad lengths, pointers, density encodings, or table IDs can cause wrong allocations or wrong geometry; the code bounds cached SFDP to one page but parser-specific reads still rely on header lengths. Optional table failures are intentionally non-fatal, so partially correct configuration is possible. SMPT detection temporarily changes read settings and executes vendor-defined reads, which can fail on controllers with limited command support. Incorrect 4BAIT handling can mask needed operations or select 4-byte opcodes without complete read/program/erase coverage.

## Test signals

Test SFDP signature fallback, BFPT-only devices, JESD216A/B/C/D differences, non-uniform erase maps, 4BAIT large flashes, xSPI Profile 1 octal-DTR flashes, malformed/truncated SFDP tables, optional table parse failures, and debugfs/sysfs SFDP cache visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sfdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sfdp.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sfdp.h

## Purpose

`sfdp.h` defines the JEDEC SFDP constants and packed structures shared by the SFDP parser and manufacturer fixups. It gives symbolic names to BFPT DWORD fields, revision values, 4-byte address mode bits, quad-enable encodings, octal read fields, command-extension bits, and parameter header layout.

## Important APIs, types, and functions

The header provides `SFDP_DWORD()` for converting one-based SFDP DWORD numbering to C array indexes and `SFDP_MASK_CHECK()` for checking multi-bit capability sets. `struct sfdp_bfpt` holds up to 20 BFPT DWORDs. `struct sfdp_parameter_header` represents an SFDP parameter header including table ID bytes, revision, length, and 24-bit table pointer.

Macro groups cover BFPT DWORD 1 address/read capability bits, DWORD 5 2-2-2/4-4-4 read support, DWORD 11 page size, DWORD 15 QER values, DWORD 16 4-byte address mode and soft reset, DWORD 17 octal STR read settings, and DWORD 18 8D command extension and byte-order flags.

## Control flow

The header has no runtime control flow, but its constants drive switch statements and field extraction in `sfdp.c` and targeted manufacturer fixups such as GigaDevice, ISSI, and Macronix post-BFPT hooks.

## State and persistence behavior

No state is stored here. The constants describe persistent capabilities encoded by flash-resident SFDP tables. The parser turns those values into mutable runtime driver state.

## Dependencies and integration points

It depends on Linux bit macros and is included by `core.h`, making these definitions available throughout the SPI NOR internals. Manufacturer files use BFPT macros to interpret data passed into post-BFPT hooks.

## Risks

A wrong mask or shift changes global SFDP interpretation. Because SFDP documentation numbers DWORDs from 1 while arrays start at 0, `SFDP_DWORD()` must be used consistently. New JESD216 revisions may add fields not represented here; unsupported values, such as 16-bit opcodes, must remain safely rejected or ignored by the parser.

## Test signals

Parser tests should cover each defined QER value, address-byte encoding, 4-byte mode encoding, octal read fields, command extension values, and manufacturer fixups that inspect BFPT DWORDs through these macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sfdp.h -->
