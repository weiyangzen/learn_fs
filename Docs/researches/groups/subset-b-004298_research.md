# subset-b-004298 Research

This grouped report covers the requested MTD/NAND files. Each file section is bounded with reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/xway_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/xway_nand.c

Purpose: Lantiq XWAY raw parallel NAND controller driver. It maps the SoC EBU NAND window, wires legacy `nand_chip` byte/command callbacks, configures the EBU chip-select/timing registers, scans one NAND chip, and registers the resulting MTD device.

Important APIs/types/functions: `struct xway_nand_data` owns `nand_controller`, `nand_chip`, saved EBU lock flags, and the MMIO NAND address. `xway_readb()`/`xway_writeb()` perform address-bit-based data, command, and address accesses. `xway_select_chip()` gates `EBU_NAND_CON` and serializes with global `ebu_lock`. `xway_cmd_ctrl()` emits CLE/ALE cycles and polls `NAND_WAIT_WR_C`. `xway_dev_ready()` returns `NAND_WAIT_RD`. `xway_attach_chip()` defaults unknown software ECC to Hamming. Probe/remove are `xway_nand_probe()` and `xway_nand_remove()`.

Control flow: platform probe allocates state, ioremaps resource 0, sets the DT flash node and parent device, installs legacy NAND callbacks, initializes the controller, reads optional `lantiq,cs`, programs `EBU_ADDSEL1`, `LTQ_EBU_BUSCON1`, and `EBU_NAND_CON`, sets default software ECC, calls `nand_scan(&chip, 1)`, then `mtd_device_register()`. Command flow is core raw-NAND -> legacy callbacks -> EBU address-bit strobes -> ready polling.

State and persistence: Persistent state is on NAND only; runtime state is EBU register configuration, the MTD registration, and NAND core bad-block/ECC state. The driver takes and releases `ebu_lock` around chip select to protect shared EBU register programming. Remove unregisters the MTD and calls `nand_cleanup()`.

Dependencies/integration: Depends on `linux/mtd/rawnand.h`, platform devices, OF, and Lantiq `lantiq_soc.h` helpers (`ltq_ebu_w32`, `ltq_ebu_w32_mask`, `ltq_ebu_r32`, `ebu_lock`). Integrates with device tree compatible `lantiq,nand-xway`, the raw NAND core, and normal MTD partition registration.

Risks: Busy-wait polling has no timeout in `xway_cmd_ctrl()`, so a wedged EBU can hang the caller. Only chip selects -1 and 0 are supported; unexpected selects call `BUG()`. The read buffer uses `NAND_WRITE_DATA` as the offset, which equals the read data path by macro value but is easy to misread. ECC defaults are conservative but may not match all attached boards.

Test signals: Boot a DT system with `lantiq,nand-xway`, verify EBU register setup, successful `nand_scan`, MTD registration, bad-block scan, read/write/erase through `mtd-utils`, and software Hamming ECC behavior. Compile-test coverage should include raw NAND API changes and Lantiq platform declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/xway_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/Kconfig

Purpose: Kconfig entry for the SPI NAND framework.

Important APIs/types/functions: Defines `menuconfig MTD_SPI_NAND` as a tristate named "SPI NAND device Support". It selects `MTD_NAND_CORE`, `MTD_NAND_ECC`, and `SPI_MEM`, and depends on `SPI_MASTER`.

Control flow: Build configuration enables `drivers/mtd/nand/spi/Makefile` to produce `spinand.o` when `CONFIG_MTD_SPI_NAND` is built-in or a module. Selecting the option pulls in the generic NAND core, NAND ECC support, and SPI memory operation framework required by `core.c`.

State and persistence: No runtime state. The symbol determines whether SPI NAND support is compiled and whether the driver can probe devices with compatible `"spi-nand"` or SPI ID `"spi-nand"`.

Dependencies/integration: Bridges MTD NAND and SPI controller subsystems. The selected `SPI_MEM` dependency is critical because the framework uses `struct spi_mem_op`, direct mappings, operation-size adjustment, and status polling.

Risks: Missing `SPI_MASTER` prevents SPI NAND support from being offered. Because the symbol selects dependencies, configuration changes in the NAND ECC or SPI memory subsystems can affect all vendor tables compiled into `spinand.o`.

Test signals: Kconfig tests should verify `CONFIG_MTD_SPI_NAND=m/y` compiles with SPI master support and that deselecting SPI master hides or disables the option. Build outputs should include `spinand.o` and all listed vendor object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/Makefile

Purpose: Builds the SPI NAND framework composite object.

Important APIs/types/functions: `spinand-objs := core.o otp.o` starts the composite object. The next lines add manufacturer files: AllianceMemory, ATO, Dosilicon, ESMT, FMSH, Foresee, GigaDevice, Macronix, Micron, Paragon, SkyHigh, Toshiba, Winbond, and XTX. `obj-$(CONFIG_MTD_SPI_NAND) += spinand.o` links the composite into the kernel or module.

Control flow: Kbuild compiles every listed source into `spinand.o`; `core.c` references exported manufacturer descriptors from these files through `spinand_manufacturers[]`, so missing an object breaks device matching.

State and persistence: No runtime state. The object list determines which IDs and manufacturer callbacks exist in the final SPI NAND driver.

Dependencies/integration: Integrates Kconfig symbol `CONFIG_MTD_SPI_NAND` with Kbuild. It also encodes the supported manufacturer surface for `core.c`.

Risks: Adding a new manufacturer descriptor in source without adding the object here makes it unreachable or causes link failures if referenced. Removing `otp.o` breaks vendor OTP operation hooks used by Micron and ESMT tables.

Test signals: `make M=drivers/mtd/nand/spi` or full kernel builds should confirm all objects compile and link into `spinand.o` for both module and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/alliancememory.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/alliancememory.c

Purpose: AllianceMemory SPI NAND manufacturer table and per-device ECC/OOB interpretation.

Important APIs/types/functions: Defines manufacturer ID `0x52`, read/write/update op variants, `am_get_eccsize()`, `am_ooblayout_ecc()`, `am_ooblayout_free()`, `am_ecc_get_status()`, one `spinand_info` entry for `AS5F34G04SND`, and exported `alliancememory_spinand_manufacturer`.

Control flow: During ID match, `core.c` selects the fastest supported cache operations, installs `am_ooblayout`, and uses `am_ecc_get_status()` after page reads. ECC status maps no errors to 0, corrected states to 3/7 or 4/8 depending on OOB size, and errored state to `-EBADMSG`.

State and persistence: No private runtime allocation. Persistent media characteristics are encoded as `NAND_MEMORG(1, 2048, 128, 64, 4096, 80, 1, 1, 1)` and `NAND_ECCREQ(4, 512)`.

Dependencies/integration: Uses SPI NAND core descriptor macros and MTD OOB layout callbacks. `SPINAND_HAS_QE_BIT` lets the core enable quad I/O when selected operation variants need it.

Risks: `am_get_eccsize()` only accepts OOB sizes 64, 128, and 256; unsupported geometry returns `-EINVAL`. The free OOB region reserves two BBM bytes, but the source comments note uncertainty about exact bad-block marker usage and unprotected chunking.

Test signals: Probe `AS5F34G04SND`, verify quad read/write path if controller supports it, inspect `mtd->oobavail`, run raw and auto-OOB read/write tests, and inject status values to validate corrected/failed ECC accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/alliancememory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/ato.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/ato.c

Purpose: ATO SPI NAND manufacturer support for `ATO25D1GA`.

Important APIs/types/functions: Defines manufacturer ID `0x9b`, common read/write/update op variants, `ato25d1ga_ooblayout_ecc()`, `ato25d1ga_ooblayout_free()`, one `spinand_info`, and exported `ato_spinand_manufacturer`.

Control flow: The core matches READID method opcode-address ID `0x12`, sets 2 KiB page/64-byte OOB geometry and 1-bit per 512-byte ECC requirement, and installs the ATO OOB layout. There is no custom ECC status function, so common SPI NAND status bits are interpreted by `spinand_check_ecc_status()`.

State and persistence: No private state. OOB layout divides the 64-byte spare area into four 16-byte sections, with 8 ECC bytes per section and free bytes before ECC; section 0 reserves byte 0 for the bad-block marker.

Dependencies/integration: Integrated through `spinand_manufacturer` descriptor in `core.c`; uses `SPINAND_HAS_QE_BIT` for quad variants.

Risks: The first free OOB region reserves only one BBM byte, unlike drivers that reserve two. Any device variant with a different BBM convention or ECC status encoding would need a new descriptor/callback.

Test signals: Confirm ID match, OOB region enumeration for sections 0 through 3, MTD read/write with on-die ECC, raw OOB behavior, and quad-enable negotiation on controllers with/without 4-bit data support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/ato.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/core.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/core.c

Purpose: Generic SPI NAND framework driver. It probes SPI memory devices, identifies manufacturer/device tables, configures bus operation templates, exposes MTD read/write/erase/bad-block/OTP operations, manages ECC and OOB layout, and registers the MTD device.

Important APIs/types/functions: Register helpers include `spinand_read_reg_op()`, `spinand_write_reg_op()`, `spinand_upd_cfg()`, `spinand_select_target()`, and `spinand_wait()`. I/O helpers include `spinand_read_page()`, `spinand_write_page()`, `spinand_mtd_read()`, `spinand_mtd_write()`, `spinand_erase()`, `spinand_isbad()`, and dirmap creation helpers. Detection and setup are `spinand_id_detect()`, `spinand_match_and_init()`, `spinand_detect()`, `spinand_configure_chip()`, `spinand_init_flash()`, `spinand_init()`, `spinand_probe()`, and `spinand_remove()`. It exports common helpers used by vendor files.

Control flow: Probe allocates `struct spinand_device`, initializes SSDR templates, resets the chip, tries three READID methods, matches a manufacturer table, selects supported cache operation variants, optionally prepares ODTR templates, allocates page/OOB buffers and config cache, runs manufacturer init/configure hooks, unlocks all blocks, initializes `nanddev` and on-die ECC, creates SPI memory direct mappings, installs MTD callbacks, registers the MTD, and later cleans up in reverse order. Reads select normal or continuous-read path, prepare ECC, load page to cache, wait for ready, read through dirmap, save/check ECC status, and update `retlen`/stats. Writes prepare ECC, write-enable, load cache, program-execute, wait, and check program-fail status. Erase write-enables, sends block erase, waits, and checks erase-fail status.

State and persistence: Runtime state includes the mutex, current target, per-target config cache, selected SDR/ODTR operation templates, direct map descriptors per plane, data/OOB/scratch buffers, continuous-read capability, manufacturer pointer, OTP descriptors, read-retry callbacks, and ECC context. Persistent media state includes NAND pages/OOB, bad-block markers, block-lock registers, configuration bits, and OTP/protection areas.

Dependencies/integration: Depends on `linux/mtd/spinand.h`, generic NAND core, MTD core, ECC engine APIs, SPI and SPI-MEM APIs. Integrates all manufacturer descriptors listed in `spinand_manufacturers[]`, OF compatible `"spi-nand"`, SPI device ID `"spi-nand"`, and MTD device registration/partition parsing.

Risks: Correctness depends on vendor tables accurately describing geometry, ECC status bits, OOB layout, target selection, and read-retry behavior. Continuous-read is disabled on controller short reads, but until then CS toggling or boundary mistakes can corrupt stream order. Config cache must stay synchronized across target changes and resume. Raw access may be unsupported for some chips. `spinand_match_and_init()` silently falls back to SSDR when ODTR setup is not fully supported, which is intentional but should be visible in performance testing.

Test signals: Probe known devices for every manufacturer table, verify all READID methods, run `mtd-utils` read/write/erase/bad-block/OOB tests, exercise raw and auto-OOB modes, verify ECC stats and `-EBADMSG`, test read-retry devices, suspend/resume from ODTR and SSDR, continuous-read fallback on controllers with partial dirmap reads, multi-plane dirmaps, multi-target chips, and OTP user/factory callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/dosilicon.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/dosilicon.c

Purpose: Dosilicon SPI NAND table for DS35Q1GA and DS35M1GA.

Important APIs/types/functions: Defines manufacturer ID `0xe5`, common cache op variants, `ds35xx_ooblayout_ecc()`, `ds35xx_ooblayout_free()`, `ds35xx_ooblayout`, two `spinand_info` entries, and `dosilicon_spinand_manufacturer`.

Control flow: Core READID opcode-dummy matches IDs `0x71` and `0x21`, selects supported cache ops, enables quad when needed, and uses generic SPI NAND ECC status interpretation with the Dosilicon OOB layout.

State and persistence: No private state. Both entries describe 2 KiB page, 64-byte OOB, 64 pages per block, 1024 blocks, and ECC requirement 4 bits per 512 bytes.

Dependencies/integration: Descriptor-only integration with SPI NAND core. OOB layout exposes four sections, each with 8 ECC bytes at offset `8 + section * 16`; free bytes reserve two BBM bytes in section 0 and use 8 bytes in later sections.

Risks: No custom ECC status callback means the generic status mask must match the chips. Section count and fixed OOB layout assume 64-byte OOB geometry.

Test signals: ID match for both parts, OOB layout section enumeration, quad path negotiation, ECC stats under corrected/uncorrectable reads, and compile coverage when manufacturer arrays change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/dosilicon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/esmt.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/esmt.c

Purpose: ESMT SPI NAND support, including devices that report either ESMT manufacturer ID `0x8c` or GigaDevice-like ID `0xc8`, plus ESMT-specific OOB and OTP handling.

Important APIs/types/functions: Defines `f50l1g41lb_ooblayout_ecc()`, `f50l1g41lb_ooblayout_free()`, OTP info callbacks, `f50l1g41lb_otp_lock()`, user/factory OTP ops, `esmt_8c_spinand_table`, `esmt_c8_spinand_table`, and two exported manufacturer descriptors.

Control flow: Core matches either manufacturer descriptor, installs the ESMT OOB layout, and for selected chips attaches user/factory OTP ops. OTP lock enters OTP/protect mode through config bits, performs write-enable and program-execute sequence, waits for completion, checks program-fail, then clears OTP mode.

State and persistence: No private allocation. Persistent state includes OTP pages and lock/protect bits in the chip configuration. The OOB layout intentionally exposes only small non-ECC-protected free chunks because some filesystems partially program OOB cleanmarkers.

Dependencies/integration: Uses SPI-MEM operations directly in the OTP lock path and shared SPI NAND OTP helpers from `otp.c`. Integrated through both `esmt_8c_spinand_manufacturer` and `esmt_c8_spinand_manufacturer` in `core.c`.

Risks: `f50l1g41lb_otp_lock()` appears to return early when `spinand_upd_cfg()` succeeds, so the later write-enable/program path is unreachable on that success path; that deserves scrutiny against upstream intent. The function also treats successful `spi_mem_exec_op()` calls as a jump to cleanup in two places, which is suspicious control flow. ESMT ID overlap with GigaDevice requires careful table ordering and IDs.

Test signals: Probe all ESMT IDs, verify OOB free/ECC bytes, read/write factory/user OTP where supported, test OTP lock persistence after power cycle, validate status/prog-fail handling, and run JFFS2/UBI OOB cleanmarker scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/esmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/fmsh.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/fmsh.c

Purpose: Fudan Micro/FMSH SPI NAND support for FM25S01A and FM25S01BI3.

Important APIs/types/functions: Defines manufacturer ID `0xa1`, common op variants, simple no-ECC-visible OOB layout for FM25S01A, 128-byte OOB layout for FM25S01BI3, `fm25s01bi3_ecc_get_status()`, tables, and `fmsh_spinand_manufacturer`.

Control flow: Core matches opcode-dummy IDs `0xe4` or `0xd4`, selects operation variants, enables quad for FM25S01BI3, installs per-chip OOB layout, and uses the custom BI3 ECC status mapper for corrected ranges 1-3, 4-6, 7-8, and uncorrectable errors.

State and persistence: Descriptor-only state. FM25S01A exposes the whole OOB after two BBM bytes as free with no visible ECC sections. FM25S01BI3 places ECC in bytes 64-127 and free data in four 12-byte regions.

Dependencies/integration: Uses SPI NAND core descriptor macros and MTD OOB layout callbacks. Manufacturer ID `0xa1` overlaps with Paragon, so matching relies on each manufacturer's table and ID method/device IDs.

Risks: Overlapping manufacturer ID can cause match-order sensitivity if future devices share IDs. FM25S01A has no custom ECC status callback; generic interpretation must be correct. The indented `#define` lines under the ECC mask are unusual style but preprocessor-valid.

Test signals: Probe both device IDs, verify OOB layout, corrected-bit ECC accounting for BI3 status values, quad-enable behavior for BI3, and conflict testing with Paragon IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/fmsh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/foresee.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/foresee.c

Purpose: FORESEE SPI NAND support for F35SQA001G, F35SQA002G, and F35SQB002G.

Important APIs/types/functions: Defines manufacturer ID `0xcd`, common operation variants, `f35sqa002g_ooblayout`, `f35sqa002g_ecc_get_status()`, `f35sqb002g_ecc_get_status()`, chip table, and `foresee_spinand_manufacturer`.

Control flow: Core matches opcode-dummy two-byte IDs, enables quad-capable variants, installs a layout with hidden ECC/no ECC region and free OOB bytes after two BBM bytes, and maps ECC status. SQA devices use generic two-bit `STATUS_ECC_MASK` semantics but return full ECC strength on any corrected status. SQB maps a wider range where status values 2 through 6 mean 4-8 corrected bitflips.

State and persistence: No private state. Geometry entries cover 1G/2G devices with 64- or 128-byte OOB and ECC requirements of 1 or 8 bits per 512 bytes.

Dependencies/integration: Descriptor-only SPI NAND integration with MTD OOB and ECC callbacks.

Risks: `f35sqa002g_ecc_get_status()` treats any non-no-bitflips/non-corrected state as `-EBADMSG`, so reserved status values become failures. Hidden ECC layout means raw/OOB users must not expect visible ECC bytes.

Test signals: Verify ID matching for duplicate-byte IDs, `mtd->oobavail`, corrected/failed ECC status values for SQA and SQB, and quad read/write fallback on controllers without quad support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/foresee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/gigadevice.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/gigadevice.c

Purpose: GigaDevice SPI NAND manufacturer support across many GD5F families, with multiple OOB layouts, ECC status decoders, and continuous-read support for GM9 devices.

Important APIs/types/functions: Defines manufacturer ID `0xc8`, `struct gigadevice_priv`, multiple read-cache variant groups, `gd5fxgm9_get_eccsr()`, `gd5fxgm9_ecc_get_status()`, `gd5fxgm9_set_continuous_read()`, several OOB layout callbacks, status decoders for Q4XA/Q4UE/Q5XE/Q4UF families, the large `gigadevice_spinand_table`, and init/cleanup ops for private state.

Control flow: Core matches numerous opcode/address/dummy IDs, selects family-specific operation variants, installs the right ECC/OOB callbacks, and for GM9 allocates private state and provides a continuous-read config toggle. ECC status flow may use base status bits, secondary status register `0xf0`, or an ECC status register read command depending on family.

State and persistence: Private runtime state tracks continuous-read configuration for GM9. Persistent chip state includes normal-vs-continuous read config bits, status registers, OOB layout, and on-die ECC correction state.

Dependencies/integration: Uses SPI NAND core helpers, SPI-MEM direct ops for feature/ECCSR access, MTD OOB layout callbacks, and the core continuous-read path via `SPINAND_CONT_READ`.

Risks: Many families share similar names but have different status encodings and OOB layouts, so table misassignment can silently undercount bitflips or expose wrong OOB bytes. Continuous-read needs controller support for non-toggling CS and full-block dirmaps; core fallback handles `-EAGAIN` but performance and correctness should be tested on real controllers. ESMT also uses manufacturer ID `0xc8`, making match ordering important.

Test signals: Probe representative chips from each table cluster, validate each ECC decoder against datasheet statuses, test secondary/ECCSR register reads, run OOB layout enumeration for 64/128/256 OOB parts, exercise GM9 continuous read and fallback, and run multi-page MTD reads under UBI-like patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/gigadevice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/macronix.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/macronix.c

Purpose: Macronix SPI NAND support for MX31/MX35 LF/UF families, including custom ECC status reads, continuous-read toggling, read-retry modes, and manufacturer initialization.

Important APIs/types/functions: Defines manufacturer ID `0xc2`, `struct macronix_priv`, `macronix_get_eccsr()`, `macronix_ecc_get_status()`, `macronix_set_cont_read()`, `macronix_set_read_retry()`, `macronix_spinand_init()`, cleanup, one OOB layout, and a large `macronix_spinand_table`.

Control flow: Core matches device IDs, selects cache op variants, and installs per-chip ECC/OOB callbacks plus optional `SPINAND_CONT_READ` and `SPINAND_READ_RETRY`. Macronix status handling reads ECCSR when threshold status is reported, extracting last-page and accumulated-page bitflip counts. Init allocates private data and may set bitflip threshold configuration for selected devices; cleanup frees it.

State and persistence: Private state records read-retry/continuous-read related data. Persistent chip state includes continuous-read config bit, read-retry feature register `0x70`, and bitflip threshold register `REG_CFG_BFT`.

Dependencies/integration: Uses SPI NAND exported register helpers and SPI-MEM ops, integrates with core continuous-read and read-retry loops, and uses MTD OOB layout callbacks.

Risks: Read-retry and ECCSR interpretation directly affect data-retention recovery and ECC stats; incorrect mode reset after retry could leave the chip in a non-default read mode. Continuous-read has the same CS/dirmap risks as GigaDevice. Threshold programming in init must be compatible with every table entry that receives it.

Test signals: Validate all IDs, ECCSR reads on threshold statuses, read-retry loop recovery and reset to mode 0, continuous-read enable/disable around MTD reads, bitflip threshold register programming, OOB availability, and suspend/resume returning to usable config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/macronix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/micron.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/micron.c

Purpose: Micron SPI NAND table and special handling for multi-die selection, Micron ECC status encoding, OOB layouts, and MT29F2G01ABAGD OTP regions.

Important APIs/types/functions: Defines manufacturer ID `0x2c`, Micron ECC status masks, `micron_8_ooblayout`, `micron_4_ooblayout`, `micron_select_target()`, `micron_8_ecc_get_status()`, `mt29f2g01abagd_otp_is_locked()`, OTP info/lock ops, `micron_spinand_table`, `micron_spinand_init()`, and exported `micron_spinand_manufacturer`.

Control flow: Core matches Micron IDs, installs x1/x4/quadio cache variants, attaches target selection for multi-die parts, sets OTP descriptors for ABAGD, and calls manufacturer init. Target selection writes the die-select register. OTP info reads the first user OTP page to infer lock state, while OTP lock sets config OTP/lock bits and uses shared read/write helpers.

State and persistence: Runtime state is descriptor-driven with no large private object. Persistent state includes selected die register, OTP pages and lock state, feature/config bits, and OOB metadata. OOB layouts differ between 4-bit and 8-bit ECC generations.

Dependencies/integration: Uses shared `otp.c` helpers, SPI NAND register helpers, MTD OOB callbacks, and `SPINAND_SELECT_TARGET` so core target changes call Micron logic.

Risks: Multi-target parts must reliably switch die before reads/writes/erases; stale target selection risks cross-die corruption. OTP lock-state detection depends on reading a page pattern and can be sensitive to raw-read support and ECC mode. ECC decoder returns range upper bounds, so wear layers may react conservatively.

Test signals: Multi-die read/write/erase across target boundaries, OTP info/read/write/lock persistence, Micron ECC status decoding for 1-3/4-6/7-8/uncorrectable, OOB layout tests, and init behavior for parts requiring quad enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/micron.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/otp.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/otp.c

Purpose: Shared SPI NAND OTP/protected-register support for factory and user one-time-programmable regions.

Important APIs/types/functions: Exposes `spinand_otp_page_size()`, `spinand_fact_otp_size()`, `spinand_user_otp_size()`, `spinand_fact_otp_read()`, `spinand_user_otp_read()`, `spinand_user_otp_write()`, and `spinand_set_mtd_otp_ops()`. Internal helpers include bound checks, `spinand_otp_rw()`, MTD OTP info/read/write/erase/lock wrappers, and mutex-protected dispatch.

Control flow: Size helpers compute pages times page+OOB size. Generic OTP read/write validates bounds, enables `CFG_OTP_ENABLE`, builds raw `nand_page_io_req` requests starting at layout start page plus offset-derived page, loops page by page through `spinand_read_page()` or `spinand_write_page()`, updates `retlen`, and disables OTP mode. `spinand_set_mtd_otp_ops()` maps vendor-provided factory/user ops into MTD protected register callbacks.

State and persistence: Runtime state is only stack request state and `retlen`; operation serialization uses the SPI NAND mutex in MTD wrappers. Persistent state is chip OTP content and vendor lock/protect state. The helper temporarily toggles OTP mode in the chip configuration.

Dependencies/integration: Depends on SPI NAND core page I/O and config helpers, `struct spinand_fact_otp_ops`, `struct spinand_user_otp_ops`, MTD protected register callbacks, and vendor layouts supplied in `spinand_info`.

Risks: `spinand_otp_rw()` uses raw page mode and casts const away for writes, so devices without raw access or with special OTP ECC rules need vendor overrides. Clearing OTP mode failure converts the operation to `-EIO` after bytes may have been transferred. Bounds use `ofs + len`, which can overflow for extreme inputs if not constrained by caller types.

Test signals: MTD user/factory protected register info/read/write/lock/erase operations, zero-length calls, unaligned offsets spanning pages, bounds failures, OTP mode cleanup on errors, and vendor-specific OTP devices such as Micron and ESMT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/otp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/paragon.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/paragon.c

Purpose: Paragon SPI NAND support for PN26G01A and PN26G02A.

Important APIs/types/functions: Defines manufacturer ID `0xa1`, cache operation variants, `pn26g0xa_ooblayout_ecc()`, `pn26g0xa_ooblayout_free()`, `pn26g0xa_ecc_get_status()`, chip table, and `paragon_spinand_manufacturer`.

Control flow: Core matches opcode-dummy IDs `0xe1` and `0xe2`, installs a 128-byte OOB layout, and maps ECC status to no errors, 1-7 corrected, 8 corrected, or `-EBADMSG`. The free layout exposes small user bytes in sections 0-3 plus a large section 4 at offsets 64-127.

State and persistence: No private runtime state. Persistent geometry is 1G/2G with 2 KiB page, 128-byte OOB, and ECC requirement 8 bits per 512.

Dependencies/integration: Descriptor-based SPI NAND integration with MTD OOB callbacks.

Risks: Manufacturer ID overlaps FMSH. OOB section 4 exposes a large second half of OOB as free; users must ensure this is compatible with actual ECC placement on both listed chips.

Test signals: ID match despite ID overlap, OOB section enumeration through `mtd_ooblayout_*`, ECC status injection, full read/write/erase, and controller support for selected cache op variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/paragon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/skyhigh.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/skyhigh.c

Purpose: SkyHigh SPI NAND support for S35ML01G/02G/04G devices with hidden ECC and no raw access.

Important APIs/types/functions: Defines manufacturer ID `0x01`, SkyHigh ECC status values, `skyhigh_spinand_ooblayout`, `skyhigh_spinand_ecc_get_status()`, `skyhigh_spinand_init()`, table entries, and `skyhigh_spinand_manufacturer`.

Control flow: Core matches opcode-dummy IDs, installs hidden-ECC OOB layout, sets `SPINAND_NO_RAW_ACCESS`, and uses the custom ECC status mapper. Manufacturer init writes `SKYHIGH_CONFIG_PROTECT_EN` to `REG_BLOCK_LOCK` before the core unlocks all blocks.

State and persistence: Runtime state is descriptor-only. Persistent config includes block-lock/config-protect bits and hidden ECC metadata. The exposed OOB free area starts after two BBM bytes and runs to the end of visible OOB.

Dependencies/integration: Uses SPI NAND register helper in manufacturer init, and depends on core fallback from raw bad-block marker reads to place-OOB mode due to `SPINAND_NO_RAW_ACCESS`.

Risks: Raw access is explicitly unsupported, so tools/filesystems requiring raw OOB or ECC bytes may fail. Bad-block operations rely on the core fallback path. The ECC requirement uses 6 bits per 32 bytes, an unusual granularity that must be propagated correctly to MTD.

Test signals: Probe all capacities, verify manufacturer init writes block-lock protect enable, test raw-mode rejection and bad-block fallback, ECC status mapping for 1-2/3-6/uncorrectable, OOB free bytes, and standard MTD read/write/erase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/skyhigh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/toshiba.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/toshiba.c

Purpose: Toshiba/Kioxia SPI NAND support for TC58/TH58 CVG/CYG/NYG families.

Important APIs/types/functions: Defines manufacturer ID `0x98`, cache operation variants, `tx58cxgxsxraix_ooblayout_ecc()`, `tx58cxgxsxraix_ooblayout_free()`, `tx58cxgxsxraix_ecc_get_status()`, a broad `toshiba_spinand_table`, and `toshiba_spinand_manufacturer`.

Control flow: Core matches Toshiba IDs across 1.8V/3.3V and different capacity variants, installs the Toshiba OOB layout, enables quad where table flags request it, and maps ECC status. Status with normal corrected bitflips returns ECC strength, threshold status returns bitflip threshold, and uncorrectable returns `-EBADMSG`.

State and persistence: No private runtime state. Table entries encode page/OOB sizes, blocks, LUNs, and ECC requirements for multiple generations. OOB layout uses per-section ECC and free regions tailored to Toshiba spare layout.

Dependencies/integration: Descriptor-only SPI NAND integration through core manufacturer array and MTD OOB layout callbacks.

Risks: Many table entries are near-duplicates, making geometry or ID mistakes likely during maintenance. Returning threshold/strength rather than exact corrected counts is conservative but less precise. Different voltage families must not be confused in board validation.

Test signals: Probe representative CVG/CYG/NYG parts, confirm page/OOB/size reporting, ECC status threshold handling, OOB free/ECC regions, quad operation selection, and boot filesystems such as UBI on corrected-bitflip media.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/toshiba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/winbond.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/winbond.c

Purpose: Winbond SPI NAND support for W25/W35 families, including high-speed configuration, volatile configuration register writes, OOB layout variants, ECC status decoding, and multi-die target selection.

Important APIs/types/functions: Defines Winbond select-target op template/fill helper, OOB layout callbacks for W25M02GV, W25N01KV/W25N02KV, W25N01JW/W35N01JW, `w25m02gv_select_target()`, `w25n02kv_ecc_get_status()`, `w25n0xjw_hs_cfg()`, `w35n0xjw_write_vcr()`, `w35n0xjw_vcr_cfg()`, the `winbond_spinand_table`, `winbond_spinand_init()`, and `winbond_spinand_manufacturer`.

Control flow: Core matches device IDs, selects family-specific layouts and optional configure hooks. Multi-die W25M02GV target selection sends a vendor die-select operation. High-speed JW/JW-like parts configure feature/VCR registers during chip setup. Init iterates targets where needed to apply configuration.

State and persistence: Runtime state is mostly core `cur_target` plus chip configuration state. Persistent/semi-persistent state includes die-select register, volatile configuration registers, high-speed mode bits, block locks, and OOB metadata.

Dependencies/integration: Uses SPI-MEM custom ops beyond standard core templates, SPI NAND exported helpers, `SPINAND_SELECT_TARGET`, and optional `configure_chip` table hooks.

Risks: VCR/high-speed setup is bus-interface sensitive; bad configuration can make subsequent operations unreliable. Multi-die target selection must be applied before any per-target register or media operation. Several OOB layouts and ECC decoders mean table-to-part mapping must remain precise.

Test signals: Probe every listed family cluster, target-switch read/write/erase on W25M02GV, high-speed config on JW/W35 parts, ECC status mapping including W25N04KV 5-8 corrected range, OOB layout verification, and fallback on controllers that cannot support faster variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/winbond.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/xtx.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/xtx.c

Purpose: XTX SPI NAND support for XT26G/Q A and D families.

Important APIs/types/functions: Defines manufacturer ID `0x0b`, A-family and D-family ECC masks, common op variants, `xt26g0xa_ooblayout`, `xt26g0xa_ecc_get_status()`, `xt26xxxd_ooblayout`, `xt26xxxd_ecc_get_status()`, large device table, and `xtx_spinand_manufacturer`.

Control flow: Core matches opcode-address IDs, installs A- or D-family OOB/ECC callbacks, and uses quad-enable only for A-family entries that set `SPINAND_HAS_QE_BIT`. A-family ECC status uses bits 2-5 and returns exact 1-7 values where possible; D-family combines `STATUS_ECC_MASK` with high ECC bits to return 4-7 or 8 corrected.

State and persistence: No private runtime state. Table entries cover 2 KiB and 4 KiB page geometries, 64/128/256-byte OOB, and 1G/2G/4G capacities.

Dependencies/integration: Uses `linux/bitfield.h`, SPI NAND descriptor macros, and MTD OOB layout callbacks.

Risks: ECC masks differ from common SPI NAND status positions, so using the wrong table callback would misreport failures. `xt26g0xa_ooblayout_free()` reserves only byte 0 for BBM, not two bytes. D-family OOB layout treats half the OOB as ECC and half as free after two BBM bytes.

Test signals: Probe A and D family IDs, verify corrected-bit counts and `-EBADMSG` status, OOB layout for all OOB sizes, quad-enable for A parts only, and large-page 4 KiB variants under MTD read/write/erase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/xtx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nftlcore.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nftlcore.c

Purpose: NAND Flash Translation Layer block translation driver for M-Systems DiskOnChip NFTL media. It exposes an MTD NAND device as a 512-byte sector block device and implements read plus optional write/fold logic.

Important APIs/types/functions: `nftl_add_mtd()` detects DiskOnChip NAND and mounts NFTL metadata. `nftl_remove_dev()` unregisters and frees tables. `nftl_read_oob()` and `nftl_write_oob()` wrap MTD OOB access. Under `CONFIG_NFTL_RW`, `NFTL_findfreeblock()`, `NFTL_foldchain()`, `NFTL_makefreeblock()`, `NFTL_findwriteunit()`, and `nftl_writeblock()` implement allocation/folding/writes. `nftl_readblock()` resolves the latest sector copy. `nftl_tr` registers `mtd_blktrans_ops`.

Control flow: When a DiskOnChip MTD appears, the driver allocates `NFTLrecord`, calls `NFTL_mount()` from `nftlmount.c`, calculates CHS geometry, and registers a blktrans device. Reads map a logical sector to its virtual unit chain, scan replacement units using OOB sector status, remember the last `SECTOR_USED`, stop at `SECTOR_FREE`, then read that 512-byte sector or return zeroes when absent. Writes find or allocate a writable erase unit, possibly fold a long chain to reclaim blocks, then write data plus OOB sector status.

State and persistence: Runtime state includes `EUNtable`, `ReplUnitTable`, free-block counts, last free unit, CHS geometry, and MTD blktrans registration. Persistent state is NFTL OOB metadata: virtual unit numbers, replacement unit links, sector status bytes, fold marks, erase marks, and wear info. Folding rewrites chains and formats old units.

Dependencies/integration: Depends on MTD core, raw NAND type checks, DiskOnChip naming convention, blktrans, and NFTL structures in `linux/mtd/nftl.h`. Module registration is via `module_mtd_blktrans(nftl_tr)`.

Risks: The driver only accepts MTD names beginning with `"DiskOnChip"`, which is fragile but intentional legacy behavior. Write support is gated by `CONFIG_NFTL_RW` and has comments acknowledging limited wear leveling and power-loss assessment. Chain traversal uses loop guards but corrupted OOB can still lead to data loss, reserved blocks, or formatting. Geometry emulation is legacy CHS and may not match all sizes cleanly.

Test signals: Attach DiskOnChip NFTL images, verify mount and blktrans device creation, read known virtual chains, test absent sectors returning zeroes, run optional write/fold/power-fail recovery tests under `CONFIG_NFTL_RW`, validate bad/corrupt OOB handling, and check module add/remove frees both tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nftlcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nftlmount.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nftlmount.c

Purpose: NFTL mount and recovery code. It finds NFTL media headers, reconstructs virtual erase-unit chains from OOB metadata, handles interrupted folds, formats invalid/free blocks, and initializes free-block accounting.

Important APIs/types/functions: `find_boot_record()` scans for `ANAND` media headers and allocates/initializes tables. `check_free_sectors()`, `NFTL_formatblock()`, `check_sectors_in_chain()`, `calc_chain_length()`, `format_chain()`, `check_and_mark_free_block()`, and `get_fold_mark()` validate and repair media. `NFTL_mount()` performs the two-pass reconstruction.

Control flow: Mount first finds a valid media header and spare copy, validates formatted size and block ranges, allocates `EUNtable`/`ReplUnitTable`, marks BIOS/header/bad blocks reserved, and sets formatted block-device size. The first pass explores each unvisited block chain by reading UCI/OOB headers, validating logical unit numbers and replacement links, detecting fold-in-progress cases, and either formatting invalid chains or assigning the chain to `EUNtable`. Duplicate chains at the same logical address are resolved by keeping the longer chain. The second pass formats unreferenced blocks and counts free EUNs.

State and persistence: Persistent state is NFTL media header, bad-unit table derived via `mtd_block_isbad()`, erase marks, wear info, fold marks, virtual/replacement unit numbers, and per-sector status bytes. Runtime state after mount is the logical-to-physical `EUNtable`, replacement `ReplUnitTable`, `numfreeEUNs`, `LastFreeEUN`, `EraseSize`, `nb_blocks`, `lastEUN`, and `MediaHdr`.

Dependencies/integration: Called by `nftlcore.c` during MTD add. Uses MTD read/OOB/erase/bad-block APIs and NFTL structures/constants from `linux/mtd/nftl.h`.

Risks: Recovery is necessarily destructive for invalid/unreferenced chains because it formats blocks. Multiple comments flag uncertain power-failure behavior around chain formatting. Some write paths use OOB writes after erase and assume erase-mark semantics. `get_fold_mark()` returns 0 on read error, causing chain format in mount logic.

Test signals: Mount images with valid primary/spare headers, bad headers, reserved bad blocks, free blocks with/without erase marks, interrupted in-place and out-of-place folds, duplicate chains, invalid replacement loops, and unreferenced blocks. Verify free counts, selected chain lengths, wear-info preservation/increment, and bad-block marking on format failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nftlmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/Kconfig

Purpose: Configuration menu for MTD partition parsers.

Important APIs/types/functions: Defines parser symbols for BCM47XX, BCM63XX, Broadcom U-Boot, command-line partitions, OF/device-tree partitions and BCM4908/Linksys NS extensions, ImageTag, AFS, TP-Link safeloader, TRX, SharpSL, RedBoot and its options, Qualcomm SMEM, and Sercomm.

Control flow: Kernel configuration selects which parser source files are built by the companion Makefile. Some symbols select dependencies such as `CRC32` or `MTD_PARSER_IMAGETAG`; some depend on architecture/platform symbols or `COMPILE_TEST`; `MTD_OF_PARTS` defaults to y when OF is available.

State and persistence: No runtime state. The selected symbols determine which partition parsers are registered and therefore which on-flash partition tables can be discovered at boot.

Dependencies/integration: Integrates MTD partition parsing with board families and bootloader formats. Parser modules later register `struct mtd_part_parser` implementations via source files in this folder.

Risks: Misconfigured dependencies can hide parsers needed for boot media, causing missing rootfs partitions. Default-y OF parser can alter parser ordering/availability. RedBoot options affect whether unallocated regions are exposed and whether system images are forced read-only.

Test signals: Kconfig dependency tests for each platform/COMPILE_TEST combination, build coverage for every symbol as module/built-in where applicable, and boot tests with command-line, DT, RedBoot, AFS, TRX, SMEM, and vendor-specific partition maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/Makefile

Purpose: Kbuild object mapping for MTD partition parsers.

Important APIs/types/functions: Maps parser config symbols to objects: `bcm47xxpart.o`, `bcm63xxpart.o`, `brcm_u-boot.o`, `cmdlinepart.o`, composite `ofpart.o`, `parser_imagetag.o`, `afs.o`, `tplink_safeloader.o`, `parser_trx.o`, `scpart.o`, `sharpslpart.o`, `redboot.o`, and `qcomsmempart.o`. The composite OF parser adds `ofpart_core.o` and optional BCM4908/Linksys NS helpers.

Control flow: When a parser symbol is enabled, Kbuild compiles and links the matching parser into the kernel/module. Composite `ofpart` conditionally includes platform-specific child object files.

State and persistence: No runtime state. Build inclusion controls which parsers register with MTD at runtime.

Dependencies/integration: Couples `parsers/Kconfig` with source compilation. The object names correspond directly to parser registration files.

Risks: A Kconfig symbol without an object mapping results in a parser that never builds. Optional OF subobjects must remain aligned with header declarations and Kconfig symbols.

Test signals: Build matrix enabling each parser individually and in combinations, especially composite `ofpart` with and without BCM4908/Linksys NS extensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/afs.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/afs.c

Purpose: ARM Firmware Suite MTD partition parser. It scans erase blocks for AFS v1/v2 footers and creates MTD partitions for discovered firmware images.

Important APIs/types/functions: Defines v1 footer/image-info structures, `word_sum()` and `word_sum_v2()` checksums, `afs_is_v1()`, `afs_is_v2()`, `afs_parse_v1_partition()`, `afs_parse_v2_partition()`, `parse_afs_partitions()`, OF match `"arm,arm-firmware-suite"`, and `afs_parser`.

Control flow: The parser first scans every erase block and counts blocks with v1 or v2 footer magic. It allocates a partition array, scans again, and parses each matching block. V1 reads the footer at the end of the erase block, checks checksum, skips SIB type 2, masks image pointers to flash size, reads image info, validates a NUL-terminated name, and creates a partition rounded to eraseblock size. V2 reads a 12-word footer and 36-word image info, validates checksum with 32-bit or 64-bit padding, then creates partitions for described regions.

State and persistence: Runtime allocation is the partition array and duplicated partition names returned through `pparts`. Persistent state is only the AFS footer/image metadata in flash; the parser does not modify media.

Dependencies/integration: Uses MTD read APIs and `struct mtd_part_parser`, registers with `module_mtd_part_parser()`, and can be selected by OF-compatible flash nodes.

Risks: V2 parsing loops over `region_count` but writes repeatedly into the single `part` slot passed by caller, so multiple-region images may not produce multiple array entries as intended. V1 name validation checks `if (i > sizeof(iis.name))`, which does not reject the no-NUL case when `i == sizeof(iis.name)`. Address masking assumes power-of-two MTD size behavior. Parser trusts several v2 indexes after checksum.

Test signals: Images with valid/invalid v1 and v2 footer magic, checksum failures, SIB hiding, missing NUL terminator, multiple v2 regions, partial MTD reads, non-power-of-two sizes, OF parser selection, and cleanup of duplicated names on parse failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/afs.c -->
