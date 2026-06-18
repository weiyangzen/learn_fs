# Research Report: subset-b-004301

This grouped report covers the MTD SPI-NOR vendor helpers, SSFDC translation layer, MTD test modules, and selected UBI attach/block files listed for `subset-b-004301`. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/spansion.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/spansion.c

## Purpose
Implements Spansion/Cypress SPI NOR manufacturer support for the generic SPI NOR core. It supplies device table entries, manufacturer-level late initialization, and Cypress-specific fixups for address mode discovery, volatile quad enable, octal DTR transitions, page-size correction, die erase, ECC write granularity, SFDP quirks, and program/erase failure handling.

## Important APIs, Types, and Functions
The exported integration point is `const struct spi_nor_manufacturer spi_nor_spansion`, backed by `spansion_nor_parts[]` and `spansion_nor_fixups`. `struct spansion_nor_params` stores the proprietary clear-status opcode selected from `USE_CLSR` or `USE_CLPEF`. Status/error paths are handled by `spansion_nor_clear_sr()`, `spansion_nor_sr_ready_and_clear()`, and `cypress_nor_sr_ready_and_clear()`. Cypress register access is expressed through `CYPRESS_NOR_RD_ANY_REG_OP`, `CYPRESS_NOR_WR_ANY_REG_OP`, and helpers including `cypress_nor_quad_enable_volatile()`, `cypress_nor_set_addr_mode_nbytes()`, `cypress_nor_get_page_size()`, and `cypress_nor_set_octal_dtr()`. Part-family fixup groups include `s25fs256t_fixups`, `s25hx_t_fixups`, `s28hx_t_fixups`, and `s25fs_s_nor_fixups`.

## Control Flow
The core matches a JEDEC ID against `spansion_nor_parts[]`, parses SFDP where available, then invokes family fixups. BFPT/post-SFDP hooks correct missing or misleading SFDP data such as 4-byte address mode methods, opcode tables, volatile register offsets, page program opcodes, erase opcodes, xSPI read opcode, dummy cycles, and page size. Late init installs ready callbacks and ECC/write-size policy. During I/O polling, the ready callback reads status from one die or all Cypress dice, clears sticky error flags, disables writes after failures, and returns ready/not-ready/error to the SPI NOR core.

## State and Persistence
Most state is volatile runtime parameter mutation in `nor->params`: `addr_nbytes`, `addr_mode_nbytes`, `page_size`, `read_dummy`, `writesize`, `ready`, `quad_enable`, `set_4byte_addr_mode`, `set_octal_dtr`, and die metadata. The code deliberately prefers volatile register updates for Cypress quad and octal mode setup to reduce risk from interrupted non-volatile register writes. It allocates `params->vreg_offset` for S25FS256T and private clear-status parameters with devm-managed memory.

## Dependencies and Integration Points
This file depends on the SPI NOR core (`core.h`), `spi_mem` operation execution, SFDP fixup callbacks, status register conventions, and MTD geometry exposed through `nor->mtd`. It integrates with manufacturer registration consumed by the SPI NOR core and with multi-die Cypress register maps.

## Risks
Incorrect SFDP fixups can create wrong capacity, page size, erase opcode, or address mode behavior. Octal DTR transitions are risky because the bus protocol changes mid-operation and are validated only by JEDEC ID readback. Program/erase failures must clear status and disable writes; missing this can leave WEL set and increase corruption risk. Multi-die status polling depends on accurate `n_dice` and `vreg_offset` data.

## Test Signals
Useful signals include successful probe of listed Spansion/Cypress parts, SFDP parse logs around fixups, MTD erase/write/read tests on affected devices, failure injection that sets `SR_E_ERR` or `SR_P_ERR`, and explicit validation of 3-byte/4-byte and 8D-8D-8D transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/spansion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sst.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sst.c

## Purpose
Provides SST/Microchip SPI NOR manufacturer support. It contains the SST flash table, special global-unlock behavior for SST26VF devices, and the SST Auto Address Increment word-programming path used by older byte-programming parts.

## Important APIs, Types, and Functions
The exported manufacturer is `spi_nor_sst`. `sst_nor_parts[]` describes SST25/SST26 devices and flags such as `SPI_NOR_HAS_LOCK`, `SPI_NOR_SWP_IS_VOLATILE`, `SPI_NOR_4BIT_BP`, and `SST_WRITE`. SST26 lock integration uses `sst26vf_nor_locking_ops`, where only full-chip unlock is supported through `sst26vf_nor_unlock()` and `spi_nor_global_block_unlock()`. Legacy write handling is implemented by `sst_nor_write_data()` and `sst_nor_write()`, installed by `sst_nor_late_init()` when the table marks `SST_WRITE`.

## Control Flow
After manufacturer matching, late init either installs SST26VF locking ops through per-part fixups or replaces `mtd->_write` for SST_WRITE parts. The write path prepares and locks the NOR, enables writes, handles an odd leading byte with byte program, writes the aligned body in two-byte AAI chunks, disables writes to terminate AAI, waits for ready, and optionally writes a trailing byte. `retlen` accumulates bytes actually written before unlock/unprepare.

## State and Persistence
Runtime state is mostly transient in `nor->program_opcode` and `nor->sst_write_second`, which drive the core write command sequence. Locking state lives in device status/configuration registers; `sst26vf_nor_unlock()` refuses partial unlock and refuses unlock if `SST26VF_CR_BPNV` indicates any block is permanently locked.

## Dependencies and Integration Points
The file depends on SPI NOR core helpers for register reads, write enable/disable, wait-ready, global unlock, and generic write data. It integrates with MTD by overriding `_write` only for the affected SST devices.

## Risks
The AAI write sequence is sensitive to odd addresses, trailing bytes, and write-disable timing. Partial unlock is intentionally unsupported for SST26VF, so callers expecting range locking get `-EINVAL` or `-EOPNOTSUPP`. If retlen accounting or ready polling is wrong, callers may see partial writes or later commands may run while AAI is active.

## Test Signals
Probe SST25/SST26 devices, run MTD write/read verification on odd and even offsets, validate full-chip unlock on SST26VF parts, and confirm unsupported lock/is_locked operations return expected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/swp.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/swp.c

## Purpose
Implements default SPI NOR software write protection using status-register block-protection bits. It maps MTD lock/unlock/is_locked calls to BP/TB/SRWD status register updates and supplies backward-compatible full-chip unlock at probe.

## Important APIs, Types, and Functions
Public integration functions are `spi_nor_init_default_locking_ops()`, `spi_nor_try_unlock_all()`, and `spi_nor_set_mtd_locking_ops()`. Core helpers include `spi_nor_get_sr_bp_mask()`, `spi_nor_get_sr_tb_mask()`, `spi_nor_get_min_prot_length_sr()`, `spi_nor_get_locked_range_sr()`, `spi_nor_sr_lock()`, `spi_nor_sr_unlock()`, and `spi_nor_sr_is_locked()`. `spi_nor_sr_locking_ops` is the default `struct spi_nor_locking_ops`.

## Control Flow
The lock path reads the status register, derives the currently protected range, checks whether requested protection can be represented without unlocking other regions, calculates the BP/TB encoding, optionally sets `SR_SRWD`, and writes back with verification. Unlock performs the inverse: it only shrinks protection if the requested region can be unlocked without locking unrelated areas. MTD wrappers prepare/lock the NOR, call the selected locking op, then unlock/unprepare.

## State and Persistence
Protection state persists in status register BP bits, optional BP3 encodings, top/bottom selector bits, and SRWD. The code supports volatile-locking devices through flags supplied by part tables, but the actual persistence depends on the flash status register implementation.

## Dependencies and Integration Points
The implementation depends on `struct spi_nor` flags set by manufacturer tables and core parsing, including `SNOR_F_HAS_LOCK`, `SNOR_F_HAS_4BIT_BP`, `SNOR_F_HAS_SR_BP3_BIT6`, `SNOR_F_HAS_SR_TB`, `SNOR_F_HAS_SR_TB_BIT6`, and `SNOR_F_NO_WP`. It plugs into the MTD lock API by assigning `_lock`, `_unlock`, and `_is_locked`.

## Risks
Only contiguous top or bottom ranges can be represented; arbitrary ranges fail with `-EINVAL`. Size calculations depend on erase-sector assumptions and power-of-two BP encodings. Mis-set flags can protect the wrong end of flash or use the wrong BP3/TB bit. `spi_nor_try_unlock_all()` intentionally ignores errors, so hardware write protection may only be visible via debug logs.

## Test Signals
Exercise lock/unlock/is_locked across top, bottom, full, empty, and unrepresentable ranges. Confirm status register values after operations and run MTD write attempts against locked regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/swp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sysfs.c

## Purpose
Exposes SPI NOR identification and SFDP data through a `spi-nor` sysfs attribute group on the SPI device. This is diagnostic and introspection glue rather than flash I/O logic.

## Important APIs, Types, and Functions
Read-only text attributes are `manufacturer`, `partname`, and `jedec_id`, implemented by `manufacturer_show()`, `partname_show()`, and `jedec_id_show()`. A binary `sfdp` attribute is implemented by `sfdp_read()`. Visibility is controlled by `spi_nor_sysfs_is_visible()` and `spi_nor_sysfs_is_bin_visible()`. The exported group list is `spi_nor_sysfs_groups[]`.

## Control Flow
Sysfs show handlers recover `struct spi_nor` from `device -> spi_device -> spi_mem -> driver data` and format the requested field. `jedec_id_show()` prefers the part-table ID when present and falls back to the probed ID buffer. `sfdp_read()` uses `memory_read_from_buffer()` over `nor->sfdp->dwords`. Visibility callbacks hide missing manufacturer/name/ID/SFDP attributes.

## State and Persistence
The file does not mutate persistent state. It reflects runtime probe state stored in `nor->manufacturer`, `nor->info`, `nor->id`, and `nor->sfdp`.

## Dependencies and Integration Points
It depends on SPI, SPI MEM, sysfs, and SPI NOR core data ownership. The group is expected to be attached by the SPI NOR driver during device registration.

## Risks
The code assumes the SPI device driver data is a valid `spi_mem` and that `spi_mem` driver data is a valid `spi_nor`. Visibility checks prevent most null dereferences for optional fields, but `sfdp_read()` assumes `nor->sfdp` exists because the binary visibility callback hides it otherwise.

## Test Signals
After probing SPI NOR devices, verify `/sys/.../spi-nor/manufacturer`, `partname`, `jedec_id`, and optional `sfdp` contents and permissions. Test devices without SFDP or table IDs to confirm attributes are hidden or fall back correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/winbond.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/winbond.c

## Purpose
Provides Winbond SPI NOR manufacturer support, including a large Winbond part table, SFDP corrections, multi-die readiness handling, extended address register cleanup, and Winbond OTP operation wiring.

## Important APIs, Types, and Functions
The exported manufacturer is `spi_nor_winbond`. `winbond_nor_parts[]` records W25X/W25Q/W25M/W25H variants, feature flags, fallback no-SFDP capabilities, and OTP layouts. Fixups include `w25q128_post_bfpt_fixups()` for a Zetta clone with incorrect SFDP size, `w25q256_post_bfpt_fixups()` to distinguish W25Q256JV 4-byte opcodes, and `winbond_nor_multi_die_post_sfdp_fixups()` to install multi-die status polling. `winbond_nor_set_4byte_addr_mode()` wraps generic EN4B/EX4B and clears EAR on exit through `winbond_nor_write_ear()`. `winbond_nor_otp_ops` maps to security-register OTP helpers.

## Control Flow
After matching a part, BFPT fixups patch size or 4-byte opcode flags. Multi-die parts compute `n_dice` from capacity and replace the ready callback with `winbond_nor_multi_die_ready()`, which selects each die and polls status. Late init installs OTP ops when an OTP organization exists and always overrides the set-4-byte-address-mode callback with the Winbond-specific wrapper.

## State and Persistence
The file mutates runtime params (`n_dice`, `ready`, `otp.ops`, `set_4byte_addr_mode`) and may write persistent/volatile device registers: die select, EN4B/EX4B, and the Extended Address Register. Clearing EAR after leaving 4-byte mode avoids stale high-address reads in subsequent 3-byte mode.

## Dependencies and Integration Points
It depends on `spi_mem` operation construction, SPI NOR core read/write register helpers, OTP security register helpers, and BFPT/SFDP parse callbacks. It integrates through the manufacturer table consumed by the SPI NOR core.

## Risks
Several Winbond variants share JEDEC IDs, so SFDP version heuristics are used to distinguish behavior. Multi-die readiness depends on die-select command support and a correct dice count. Clearing EAR requires write enable and write disable; failure can leave 3-byte reads mapped to the wrong 16 MiB window.

## Test Signals
Probe representative Winbond devices, especially W25Q128 clone, W25Q256FV/JV, and multi-die W25Q01/W25Q02 parts. Validate 4-byte exit followed by low-address 3-byte reads, OTP read/write/lock behavior, and die-by-die ready polling during long erase/program operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/winbond.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/xmc.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/xmc.c

## Purpose
Registers XMC (Wuhan Xinxin Semiconductor Manufacturing Corp.) SPI NOR parts with the generic SPI NOR core.

## Important APIs, Types, and Functions
The only exported object is `spi_nor_xmc`. It references `xmc_nor_parts[]`, which contains `XM25QH64A` and `XM25QH128A` entries with JEDEC IDs, sizes, 4 KiB sectors, dual-read, and quad-read no-SFDP capability flags.

## Control Flow
The SPI NOR core matches the manufacturer and JEDEC ID, then uses the static part metadata if SFDP data is missing or insufficient. There are no custom fixups, callbacks, or register operations.

## State and Persistence
No runtime or persistent state is changed by this file. All behavior is declarative through the flash table.

## Dependencies and Integration Points
It depends on `linux/mtd/spi-nor.h` and the local SPI NOR core definitions. Integration is via the manufacturer registry in the SPI NOR subsystem.

## Risks
The risk is stale or incomplete part metadata. If newer XMC variants share IDs or require fixups, this table alone cannot handle them.

## Test Signals
Probe both listed XMC parts and verify capacity, erase size, dual read, quad read, and fallback operation on systems without usable SFDP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/xmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ssfdc.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/ssfdc.c

## Purpose
Implements a read-only SSFDC/SmartMedia flash translation layer as an MTD block translation driver. It detects SSFDC-formatted small-page NAND, builds a logical-to-physical block map from OOB metadata, and exposes a read-only block device.

## Important APIs, Types, and Functions
`struct ssfdcr_record` extends `mtd_blktrans_dev` with CHS geometry, CIS block, erase size, logical block map, and map length. Detection and mapping are handled by `get_valid_cis_sector()`, `read_raw_oob()`, `get_logical_address()`, and `build_logical_block_map()`. Block translation hooks are `ssfdcr_add_mtd()`, `ssfdcr_remove_dev()`, `ssfdcr_readsect()`, and `ssfdcr_getgeo()`, registered through `ssfdcr_tr`.

## Control Flow
On module init, `register_mtd_blktrans()` installs the translator. For each MTD, `ssfdcr_add_mtd()` accepts only NAND with 16-byte OOB and size within `UINT_MAX`, finds the CIS/IDI signature, allocates state, computes geometry, allocates an all-`0xffff` logical map, scans physical blocks after the CIS block, reads OOB address fields, validates signature/parity, stores logical-to-physical mappings by zone, and registers the block device. Reads compute logical block and sector offsets, translate through the map, read the physical 512-byte sector, or return `0xff` for unmapped logical sectors.

## State and Persistence
Persistent state is on-flash SSFDC CIS and OOB logical address metadata. Runtime state is the allocated logical block map and geometry cached in `ssfdcr_record`. The driver is read-only and does not update flash metadata.

## Dependencies and Integration Points
It depends on MTD core, raw NAND bad block checks, OOB reads, and `mtd_blktrans` block translation. It registers major 257 with three partition bits.

## Risks
The CIS detection loop appears to read when `mtd_block_isbad()` returns true, which is a sensitive area to verify against intended semantics. The mapper trusts OOB logical address metadata and overwrites duplicate logical entries with the latest scanned physical block. `BUG_ON(block_address >= map_len)` can crash on out-of-range block device reads. This legacy read-only FTL assumes small-page SmartMedia geometry.

## Test Signals
Test with known SSFDC images and malformed OOB metadata. Verify block reads, unmapped sectors returning `0xff`, CHS geometry, bad block skipping, and non-SSFDC NAND rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ssfdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/tests/Makefile

## Purpose
Builds optional MTD kernel test modules when `CONFIG_MTD_TESTS` is enabled.

## Important APIs, Types, and Functions
The Makefile adds modules for OOB, page, read, speed, stress, subpage, torture, NAND ECC, and NAND bit error tests. It also links `mtd_test.o` into each module through repeated `obj-$(CONFIG_MTD_TESTS)` lines and per-module `*-objs` assignments.

## Control Flow
Kbuild evaluates `CONFIG_MTD_TESTS`; when enabled it builds the listed module objects. Per-module object lists map module names such as `mtd_oobtest` to source files such as `oobtest.o`.

## State and Persistence
No runtime state exists. Build output and module availability are controlled by kernel configuration.

## Dependencies and Integration Points
This integrates the test sources into Kbuild under the MTD subsystem. The helper object `mtd_test.o` exports common symbols used by most test modules.

## Risks
Because `mtd_test.o` is listed repeatedly in `obj-*`, build behavior depends on Kbuild handling shared object linkage as intended. Enabling these modules exposes destructive tests that can erase user-selected MTD devices.

## Test Signals
Run kernel builds with `CONFIG_MTD_TESTS=m` or `y` and confirm all expected modules are produced and link against `mtd_test` helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/mtd_nandecctest.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/tests/mtd_nandecctest.c

## Purpose
Self-tests software Hamming NAND ECC correction/detection logic without requiring an MTD device. It covers no-error, correctable single-bit data/ECC errors, and detectable double-bit scenarios for 256-byte and 512-byte data blocks.

## Important APIs, Types, and Functions
`struct nand_ecc_test` defines each prepare/verify pair. Error injection helpers include `single_bit_error_data()`, `double_bit_error_data()`, `single_bit_error_ecc()`, and `double_bit_error_ecc()`. Verification uses `ecc_sw_hamming_calculate()` and `ecc_sw_hamming_correct()`. `nand_ecc_test_run()` allocates buffers, generates random data, runs `nand_ecc_test[]`, and dumps diagnostic data on failure.

## Control Flow
`ecc_test_init()` runs the suite for 256 and 512 byte blocks. For each case the module generates correct data/ECC, applies a prepared corruption pattern, recalculates ECC, checks whether correction returns the expected code, and verifies data contents. If raw NAND support is disabled, the run function is stubbed to success.

## State and Persistence
No flash state is touched. Runtime buffers are allocated per test run and freed before returning. Random data and random bit positions make coverage variable across loads.

## Dependencies and Integration Points
It depends on `CONFIG_MTD_RAW_NAND`, `CONFIG_MTD_NAND_ECC_SW_HAMMING_SMC`, the NAND ECC software Hamming implementation, kernel random APIs, and `mtdtest_relax()`.

## Risks
Randomized bit positions can make exact failures non-reproducible unless logs are captured. The test only covers Hamming ECC behavior and not controller-specific ECC engines or real OOB layouts.

## Test Signals
Loading the module should print `ok` lines for each case/size. Failures dump corrupted and correct data/ECC buffers and return an error from module init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/mtd_nandecctest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/mtd_test.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/tests/mtd_test.c

## Purpose
Provides shared helper functions for MTD test modules: erase an eraseblock, scan bad blocks, erase only good blocks, and perform full-length checked reads/writes.

## Important APIs, Types, and Functions
Exported GPL symbols are `mtdtest_erase_eraseblock()`, `mtdtest_scan_for_bad_eraseblocks()`, `mtdtest_erase_good_eraseblocks()`, `mtdtest_read()`, and `mtdtest_write()`. `is_block_bad()` wraps `mtd_block_isbad()` and logs bad eraseblocks.

## Control Flow
Erase helpers build `struct erase_info` and call `mtd_erase()`. Bad-block scanning skips devices that cannot have bad blocks and otherwise fills a caller-provided bad-block table. Read/write helpers call MTD core APIs, treat corrected bitflips as successful reads, enforce full transfer length, and log failing addresses.

## State and Persistence
The helper can erase and write flash through callers. It does not maintain its own persistent state; caller-owned BBT arrays hold scan results.

## Dependencies and Integration Points
All destructive test modules include `mtd_test.h` and link to these exported helpers through the test Makefile. It depends on MTD core APIs and kernel scheduling/printk support.

## Risks
Helpers perform real erase/write operations and rely on callers to restrict device and range. `mtdtest_read()` masks corrected bitflip returns, which is appropriate for tests that care about data correctness but hides ECC correction counts.

## Test Signals
Build/link tests should resolve exported symbols. Runtime signals are logs for erase/read/write failures and correct BBT population on NAND devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/mtd_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/mtd_test.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/tests/mtd_test.h

## Purpose
Declares shared MTD test helper APIs and supplies a cooperative abort point used by long-running test modules.

## Important APIs, Types, and Functions
`mtdtest_relax()` calls `cond_resched()` and aborts with `-EINTR` if the current task has a pending signal. The header declares the erase, BBT scan, read, and write helpers exported from `mtd_test.c`.

## Control Flow
Test loops call `mtdtest_relax()` between eraseblocks or operations to keep the kernel responsive and allow module load/init to abort when signaled.

## State and Persistence
The header has no persistent state. It observes pending task signals and returns an error to the caller.

## Dependencies and Integration Points
It depends on `linux/mtd/mtd.h` and `linux/sched/signal.h`. It is included by the MTD test modules.

## Risks
Callers must actually check and propagate `mtdtest_relax()` errors; otherwise long destructive tests may remain hard to interrupt. The helper declarations must stay in sync with exported implementations.

## Test Signals
Compile coverage validates declarations. Runtime cancellation can be tested by interrupting long-running modules and confirming `-EINTR` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/mtd_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/nandbiterrs.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/tests/nandbiterrs.c

## Purpose
Tests NAND ECC recovery by using one selected page and either injecting increasing bit errors or repeatedly overwriting the same pattern until physical bit errors appear.

## Important APIs, Types, and Functions
Module parameters are `dev`, `page_offset`, `seed`, and `mode`. Helpers include `hash()` for deterministic page data, `write_page()`, `rewrite_page()` using raw `mtd_write_oob()` without ECC/OOB writes, `read_page()` which measures corrected ECC count via `mtd->ecc_stats`, `verify_page()`, `insert_biterror()`, `incremental_errors_test()`, and `overwrite_test()`.

## Control Flow
Init opens the selected MTD, requires NAND, calculates target offset/eraseblock/subpage layout, allocates one-page buffers, erases the block, runs the selected mode, then erases the block again on success. Incremental mode writes known data, raw-rewrites progressively corrupted data with one additional cleared bit per subpage, reads through ECC, and stops when read fails. Overwrite mode repeatedly writes the same data and records a corrected-bit histogram until failure or `max_overwrite`.

## State and Persistence
The test erases and rewrites the target eraseblock. It intentionally leaves the block unerased on failure for inspection. Runtime state includes page buffers, selected offset, subpage counts, and ECC stat deltas.

## Dependencies and Integration Points
Depends on NAND MTD semantics, raw OOB write support, ECC stats, and shared `mtd_test` helpers.

## Risks
This is destructive for the selected eraseblock. Raw writes bypass ECC and may depend on controller support. The init path sets `err = -EIO` after success before printing success, so module load behavior should be checked carefully against expected test-module conventions.

## Test Signals
Logs show corrected bit counts, ECC failure thresholds, histograms, and final success/failure. Run on expendable NAND pages only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/nandbiterrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/oobtest.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/tests/oobtest.c

## Purpose
Destructively tests NAND OOB read/write behavior across whole-device writes, block-wide OOB transfers, varying offsets/lengths, bounds checks, and cross-eraseblock OOB reads/writes.

## Important APIs, Types, and Functions
Module parameters are `dev` and `bitflip_limit`. Core helpers are `write_eraseblock()`, `write_whole_device()`, `verify_eraseblock()`, `verify_eraseblock_in_one_go()`, `verify_all_eraseblocks()`, `memcmpshowoffset()`, and `memffshow()`. The module uses `struct mtd_oob_ops` in `MTD_OPS_AUTO_OOB` mode with data length zero.

## Control Flow
Init validates `dev`, requires NAND, allocates buffers/BBT, scans bad blocks, then runs five tests. It erases good blocks before major write phases, writes deterministic pseudo-random OOB bytes, verifies them page-by-page or in one transfer, tests variable OOB offset/length, confirms reads/writes past OOB/device ends fail, and verifies OOB access spanning the boundary between neighboring good eraseblocks.

## State and Persistence
The module erases and writes OOB data across the selected whole MTD device, skipping bad blocks. `errcnt` accumulates verification failures; pseudo-random seeds make expected data deterministic.

## Dependencies and Integration Points
Depends on NAND OOB availability, MTD OOB API, bad-block handling, prandom state, and shared MTD test helpers.

## Risks
This test wipes the specified MTD device. It assumes `mtd->oobavail` and page/eraseblock geometry are stable. Bitflip tolerance can hide small OOB differences if `bitflip_limit` is set. Some controllers may restrict OOB operations differently, producing expected failures.

## Test Signals
Successful logs progress through "test 1 of 5" to "test 5 of 5" and finish with zero errors. Boundary and out-of-range tests should explicitly log expected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/oobtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/pagetest.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/tests/pagetest.c

## Purpose
Destructively tests NAND page read/write correctness, page boundary behavior, read data-register isolation, erase effects, and eraseblock cross-interference.

## Important APIs, Types, and Functions
Module parameter `dev` selects the MTD. Helpers include `write_eraseblock()`, `verify_eraseblock()`, `crosstest()`, `erasecrosstest()`, and `erasetest()`. Buffers include one eraseblock of random data, two-page read buffers, a boundary expected buffer, and a BBT.

## Control Flow
Init opens a NAND MTD, computes page and eraseblock counts, allocates buffers, scans bad blocks, erases the device, writes deterministic random data to all good eraseblocks, verifies each block with two-page reads including eraseblock boundary checks, then performs crosstest, erasecrosstest when enough blocks exist, and erasetest.

## State and Persistence
The whole selected MTD is erased and rewritten. Runtime state is deterministic prandom seed, geometry values, `errcnt`, and bad-block table. The test leaves whatever final erase/write state the sequence produced.

## Dependencies and Integration Points
Depends on NAND MTD read/write/erase behavior, shared helpers, and bad-block handling. It uses two-page reads to catch controller data buffer problems.

## Risks
This test wipes data. It assumes enough good blocks for boundary and cross tests; some subtests are skipped or constrained when bad blocks occupy ends. Verification reads adjacent pages and eraseblock boundaries, so geometry misreporting can produce false failures or expose driver bugs.

## Test Signals
Progress logs for writing/verifying all eraseblocks, "crosstest ok", "erasecrosstest ok", "erasetest ok", and final zero `errcnt` indicate success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/pagetest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/readtest.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/tests/readtest.c

## Purpose
Non-writing MTD test that reads every good eraseblock page-by-page and optionally reads OOB data, reporting and dumping failing eraseblocks.

## Important APIs, Types, and Functions
Module parameter `dev` selects the MTD. `read_eraseblock_by_page()` reads page data via `mtdtest_read()` and OOB via `mtd_read_oob()` in `MTD_OPS_PLACE_OOB`. `dump_eraseblock()` prints data and OOB hex dumps on failure. Init is `mtd_readtest_init()`.

## Control Flow
Init opens the selected MTD, chooses page size (`writesize` or 512 for non-NAND), computes eraseblock/page counts, allocates data/OOB buffers and a BBT, scans bad blocks, then reads each good eraseblock page-by-page. Any failed block is dumped while the scan continues unless interrupted by `mtdtest_relax()`.

## State and Persistence
No flash writes or erases occur. Runtime state consists of buffers and a bad-block table.

## Dependencies and Integration Points
Depends on MTD read and OOB APIs plus shared helper functions. It can run on NAND and non-NAND MTD, with non-NAND using assumed 512-byte pages.

## Risks
Large failures can produce extensive kernel logs due to hex dumps. OOB reads are attempted only when `mtd->oobsize` is nonzero. Corrected bitflips are treated as successful by `mtdtest_read()`.

## Test Signals
Success prints "finished"; failure prints read/OOB error addresses and dumps the affected eraseblock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/readtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/speedtest.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/tests/speedtest.c

## Purpose
Measures erase, write, and read throughput for an MTD device using eraseblock, page, two-page, and multi-block erase access patterns.

## Important APIs, Types, and Functions
Module parameters are `dev` and optional `count`. Helpers include `multiblock_erase()`, write/read functions by eraseblock/page/two-pages, timing helpers `start_timing()`, `stop_timing()`, and `calc_speed()`. Init is `mtd_speedtest_init()`.

## Control Flow
Init opens the selected MTD, computes geometry, optionally limits eraseblock count, fills an eraseblock buffer with random data, scans bad blocks, counts good eraseblocks, and runs timed phases: eraseblock write/read, page write/read, two-page write/read, single erase, and multi-block erase sizes from 2 to 64 blocks.

## State and Persistence
The test erases and writes all selected good eraseblocks, so it destroys data. Timing state is held in `ktime_t` globals. Speed is calculated in KiB/s over good eraseblocks.

## Dependencies and Integration Points
Depends on MTD erase/read/write APIs, shared helper functions, bad-block handling, and kernel timing APIs.

## Risks
Destructive to selected range. The speed denominator uses all good eraseblocks for every phase, including multi-block erase loops that may skip around bad blocks, so results are approximate. Non-NAND devices use a 512-byte assumed page size.

## Test Signals
Logs report KiB/s for each phase and any operation errors. Repeating with different `count` values can isolate device regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/speedtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/stresstest.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/tests/stresstest.c

## Purpose
Runs random read/write/erase operations against an MTD device to stress driver state transitions and boundary handling.

## Important APIs, Types, and Functions
Module parameters are `dev` and `count` (default 10000). Helpers include `rand_eb()`, `rand_offs()`, `rand_len()`, `do_read()`, `do_write()`, and `do_operation()`. The `offsets` array tracks current written offsets per eraseblock.

## Control Flow
Init opens the device, computes geometry, requires at least two eraseblocks, allocates two-eraseblock buffers and offsets, initializes offsets as full, scans bad blocks, then runs `count` random operations. Writes erase a block when its tracked offset reaches the end, choose page-aligned lengths, erase the next block when crossing into it, and update offsets.

## State and Persistence
The test destructively writes and erases random regions. Runtime state includes random data, read buffer, BBT, and per-eraseblock write offsets. It does not verify data contents against a model, focusing on operation success/failure.

## Dependencies and Integration Points
Depends on MTD read/write/erase APIs, shared test helpers, kernel random APIs, vmalloc, and bad-block handling.

## Risks
Destructive and randomized. `rand_len()` can return zero, so some operations may be no-ops depending on MTD behavior. The test assumes two adjacent eraseblocks unless the second is bad and clamps the range.

## Test Signals
Progress logs every 1024 operations and final operation count. Any read/write/erase error aborts the module load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/stresstest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/subpagetest.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/tests/subpagetest.c

## Purpose
Destructively validates NAND subpage write/read behavior for single subpages and variable multiples of the subpage size, including erased-state verification.

## Important APIs, Types, and Functions
Module parameter `dev` selects the MTD. Helpers include `write_eraseblock()`, `write_eraseblock2()`, `verify_eraseblock()`, `verify_eraseblock2()`, `verify_eraseblock_ff()`, and `verify_all_eraseblocks_ff()`. `subpgsize` is derived from `mtd->writesize >> mtd->subpage_sft`.

## Control Flow
Init requires NAND, computes subpage and eraseblock geometry, allocates buffers sized for up to 32 subpages, scans bad blocks, erases the device, writes two subpages per good eraseblock and verifies them, erases and verifies all-`0xff`, then writes variable-size subpage multiples across each eraseblock and verifies again before a final erased-state check.

## State and Persistence
The selected MTD is erased and rewritten. Expected data is regenerated from deterministic prandom seeds. `errcnt` counts compare failures.

## Dependencies and Integration Points
Depends on NAND subpage support exposed through MTD geometry, raw MTD read/write calls, shared erase/BBT helpers, and prandom.

## Risks
Destructive. Some NAND/controllers restrict partial-page writes or require specific alignment; this test will expose those limitations. The buffer size limits variable writes to 32 subpages per operation.

## Test Signals
Success logs write/verify progress, all-`0xff` verification, and final zero errors. Failures print addresses and, for the first two subpage checks, written/read subpage dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/subpagetest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/torturetest.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/tests/torturetest.c

## Purpose
Repeatedly erases and writes selected eraseblocks to stress flash endurance and data integrity. It is explicitly dangerous and can wear out flash.

## Important APIs, Types, and Functions
Parameters include `dev`, starting `eb`, `ebcnt`, optional `pgcnt`, status `gran`, `check`, and `cycles_count`. Main helpers are `check_eraseblock()`, `write_pattern()`, `report_corrupt()`, `print_bufs()`, and `countdiffs()`. Pattern buffers hold `0xff`, alternating `0x55/0xaa`, and inverse alternating data.

## Control Flow
Init opens the MTD, validates page count, allocates patterns and bad-block table, scans the selected range, then loops until `cycles_count` expires or indefinitely by default. Each cycle erases good blocks, optionally verifies erased `0xff`, writes alternating patterns, optionally verifies them, increments cycle count, and periodically prints elapsed timing.

## State and Persistence
This test intentionally consumes erase cycles and writes selected blocks repeatedly. Runtime state includes pattern buffers, check buffer, bad-block map, and erase cycle counter. If interrupted or failed, blocks may contain the last written test pattern.

## Dependencies and Integration Points
Depends on MTD erase/read/write APIs, shared bad-block and erase helpers, kernel timing, and cooperative `mtdtest_relax()`.

## Risks
High destructive risk: it can wear out flash and destroy data. Infinite default behavior when `cycles_count` is zero requires operator care. Verification retries can distinguish transient read issues from persistent corruption but also produce large logs.

## Test Signals
Status logs show erase cycles completed and timing. Verification failures report differing pages, byte/bit counts, and detailed read-versus-written bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/tests/torturetest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/ubi/Kconfig

## Purpose
Defines kernel configuration options for UBI, the MTD layer that provides logical volumes, wear leveling, bad-block handling, optional fast attach, block-device export, fault injection, gluebi, and NVMEM exposure.

## Important APIs, Types, and Functions
The root option is `MTD_UBI`, a tristate that selects `CRC32`. Suboptions include `MTD_UBI_WL_THRESHOLD`, `MTD_UBI_BEB_LIMIT`, `MTD_UBI_FASTMAP`, `MTD_UBI_GLUEBI`, `MTD_UBI_BLOCK`, `MTD_UBI_FAULT_INJECTION`, and `MTD_UBI_NVMEM`.

## Control Flow
Kconfig gates all suboptions under `if MTD_UBI`. Defaults favor conservative behavior: Fastmap, block, fault injection, and NVMEM are disabled by default; wear leveling threshold defaults to 4096; expected bad eraseblocks defaults to 20 per 1024.

## State and Persistence
Configuration choices become build-time state and influence runtime UBI policy, including reserved PEB calculations, wear-leveling behavior, and compiled feature availability. Fastmap has on-flash format implications.

## Dependencies and Integration Points
UBI depends on MTD and CRC32. `MTD_UBI_BLOCK` depends on `BLOCK`, fault injection depends on `FAULT_INJECTION_DEBUG_FS`, and NVMEM support depends on `NVMEM`.

## Risks
Bad tuning can reserve too few PEBs or wear-level too aggressively/weakly. Fastmap is marked experimental and can affect attach behavior and on-flash metadata. Enabling gluebi or block devices exposes additional interfaces over UBI volumes.

## Test Signals
Build matrix tests should cover UBI as built-in/module, with and without Fastmap/block/gluebi/nvmem. Runtime tests should verify attach, wear-leveling policy, bad-block reservation, and option-specific devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/ubi/Makefile

## Purpose
Defines Kbuild composition for UBI core and optional UBI companion modules.

## Important APIs, Types, and Functions
`obj-$(CONFIG_MTD_UBI) += ubi.o` builds the main UBI object from `vtbl.o`, `vmt.o`, `upd.o`, `build.o`, `cdev.o`, `kapi.o`, `eba.o`, `io.o`, `wl.o`, `attach.o`, `misc.o`, and `debug.o`. Conditional objects add `fastmap.o` and `block.o`. Separate modules include `gluebi.o` and `nvmem.o`.

## Control Flow
Kbuild links feature objects into `ubi.o` according to the selected Kconfig symbols. Block support is built into UBI when `CONFIG_MTD_UBI_BLOCK` is enabled, not as a separate module.

## State and Persistence
No runtime state is held here. Build-time object inclusion determines available runtime features.

## Dependencies and Integration Points
This file maps Kconfig options from `Kconfig` to compiled implementation files in the UBI directory.

## Risks
Missing object entries can produce unresolved symbols or silently omit configured features. Because `block.o` is linked into `ubi.o`, init/exit ordering must be coordinated with UBI core build code.

## Test Signals
Kernel builds should be run across combinations of `MTD_UBI`, `MTD_UBI_FASTMAP`, `MTD_UBI_BLOCK`, `MTD_UBI_GLUEBI`, and `MTD_UBI_NVMEM` to confirm expected objects link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/attach.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/ubi/attach.c

## Purpose
Implements UBI attach-time media scanning and attach information construction. It classifies every PEB, reconstructs volume/LEB mappings, handles corruptions and power-cut cases, supports Fastmap fallback, computes erase-counter statistics, and hands the result to volume table, wear-leveling, and EBA initialization.

## Important APIs, Types, and Functions
Externally used functions include `ubi_alloc_aeb()`, `ubi_free_aeb()`, `ubi_compare_lebs()`, `ubi_add_to_av()`, `ubi_add_av()`, `ubi_find_av()`, `ubi_remove_av()`, `ubi_early_get_peb()`, and `ubi_attach()`. Internal helpers include `find_or_add_av()`, `add_to_list()`, `add_corrupted()`, `add_fastmap()`, `validate_vid_hdr()`, `check_corruption()`, `scan_peb()`, `late_analysis()`, `scan_all()`, optional `scan_fast()`, `destroy_ai()`, and `self_check_ai()`.

## Control Flow
Attach allocates `struct ubi_attach_info`, optionally tries Fastmap, and otherwise scans all PEBs. `scan_peb()` skips bad blocks, reads EC headers, classifies empty/corrupt/bitflip states, validates version and image sequence, reads VID headers, handles unsupported internal volumes by compatibility policy, classifies VID corruption using data-area checks, and either adds PEBs to free/erase/corrupt/alien/fastmap lists or into per-volume RB trees. Duplicate LEBs are resolved by `ubi_compare_lebs()`, which uses sequence numbers and copy-flag data CRCs to choose the newest valid copy. After scan, `late_analysis()` rejects excessive unexpected corruption or non-UBI-looking media, unknown ECs are normalized to mean EC, self-checks may run, and `ubi_attach()` initializes volume table, WL, and EBA subsystems.

## State and Persistence
Persistent state read from flash includes EC headers, VID headers, sequence numbers, image sequence, copy flags, data CRCs, and volume metadata. Runtime attach state consists of RB trees of volumes and LEBs plus lists for free, erase, corrupted, alien, and fastmap PEBs. The path may erase PEBs early through `ubi_early_get_peb()` and `early_erase_peb()` before WL is initialized.

## Dependencies and Integration Points
The file depends on UBI I/O helpers, CRC32, RB trees, slab caches, Fastmap when enabled, volume table reading, wear-leveling init, EBA init, debug self-checks, and MTD error classification including ECC errors/bitflips.

## Risks
Attach correctness is critical: misclassifying corruption can erase recoverable data or preserve unusable PEBs. Duplicate LEB selection relies on sequence numbers and copy CRCs. Fastmap fallback must avoid attaching stale/bad maps; bad VID headers during fast scan force full scan. Erase-counter overflow and inconsistent VID headers correctly abort attach. Resource cleanup across many error paths must preserve no leaks or stale pointers.

## Test Signals
Test clean media, empty media, power-cut interrupted erase/write, duplicate LEBs, corrupted EC/VID headers, image sequence mismatches, internal volume compatibility policies, excessive corruption rejection, Fastmap valid/invalid fallback, and debug self-check paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/block.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/ubi/block.c

## Purpose
Provides read-only block devices layered on top of UBI volumes. It supports boot/module `ubi.block=` parameters and runtime create/remove/resize through UBI notifications and ioctls elsewhere in UBI.

## Important APIs, Types, and Functions
Key types are `struct ubiblock_param`, `struct ubiblock_pdu`, and `struct ubiblock`. Public functions are `ubiblock_create()`, `ubiblock_remove()`, `ubiblock_init()`, and `ubiblock_exit()`. Request handling is done by `ubiblock_queue_rq()` and `ubiblock_read()`. Device lifecycle uses `ubiblock_open()`, `ubiblock_release()`, `ubiblock_cleanup()`, `ubiblock_resize()`, `ubiblock_notify()`, and `ubiblock_remove_all()`.

## Control Flow
The `block=` parameter parser accepts a volume path, `ubi_num,vol_id`, or `ubi_num,name`. Init registers a block major and a UBI volume notifier. When matching volumes are added or runtime create is requested, `ubiblock_create()` calculates 512-byte sector capacity, checks duplicates under `devices_mutex`, allocates a device, configures blk-mq, allocates a gendisk/minor, sets capacity, links it globally, and calls `device_add_disk()`. Reads translate sector position to UBI LEB plus offset, split requests at LEB boundaries, and call `ubi_read_sg()`. Remove refuses busy devices; resize updates disk capacity for existing devices; notifications create/remove/resize in response to UBI volume events.

## State and Persistence
Runtime state includes the global ubiblock list, IDR minor allocation, block major, parsed boot parameters, per-device refcount, UBI volume descriptor, gendisk, request queue, tag set, and LEB size. It does not persist new on-flash data and only opens UBI volumes read-only.

## Dependencies and Integration Points
Depends on UBI volume APIs, block layer and blk-mq, scatterlists, IDR, gendisk, and volume notifier infrastructure. It is conditionally compiled into `ubi.o` when `CONFIG_MTD_UBI_BLOCK` is enabled.

## Risks
Only read requests are supported; writes return I/O error. Capacity truncates non-512-byte tail bytes, with warning severity depending on dynamic/static volume type. Removal must coordinate `devices_mutex` and `dev_mutex` to avoid freeing open devices. Request completion maps UBI read errors through `errno_to_blk_status()`.

## Test Signals
Test `ubi.block=` path/name/id forms, UBI volume add/remove/resize/update notifications, read-only mount behavior, write rejection, reads spanning LEB boundaries, busy remove returning `-EBUSY`, and capacity truncation warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/block.c -->
