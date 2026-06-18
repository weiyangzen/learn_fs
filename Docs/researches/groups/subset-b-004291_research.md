# subset-b-004291 Research

Grouped research for NAND raw controller files under `sources/distributed-fs/ceph-client/drivers/mtd/nand/raw`. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/diskonchip.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/diskonchip.c

## Purpose
Implements the legacy M-Systems DiskOnChip 2000, Millennium, and Millennium Plus raw NAND driver. It probes fixed physical memory windows or a configured address, identifies DiskOnChip ASIC variants, exposes them through the raw NAND/MTD stack, and performs DiskOnChip-specific ECC, bad-block-table, NFTL, and INFTL media-header handling.

## Important APIs, Types, And Functions
`struct doc_priv` embeds `nand_controller` state plus mapped I/O address, chip/floor selection, detected geometry, media-header pages, Reed-Solomon decoder, and a `late_init()` callback. Module parameters control probing, debug output, 32-bit read probing, ECC failure suppression, automatic partitioning, firmware partition exposure, and writable INFTL BBTs. The controller hooks are `doc200x_exec_op()`, `doc2001plus_exec_op()`, and `doc200x_attach_chip()`. ECC is wired through `doc200x_enable_hwecc()`, `doc200x_calculate_ecc()`, `doc200x_correct_data()`, and `doc_ecc_decode()`, using the generic RS library with DiskOnChip syndrome conversion.

## Control Flow
`init_nanddoc()` probes either `doc_config_location` or platform address tables. `doc_probe()` reserves and maps the region, resets/enables the ASIC, checks chip ID and toggle behavior, filters aliases, allocates the NAND/private/BBT bundle, initializes RS decoding and NAND controller ops, then calls the variant initializer. `doc2000_init()`, `doc2001_init()`, and `doc2001plus_init()` select NFTL or INFTL late initialization and establish chip counts. After `nand_scan()`, `nftl_scan_bbt()` or `inftl_scan_bbt()` manually creates the BBT and registers MTD partitions built from media headers unless `no_autopart` is set.

## State And Persistence
Persistent flash state includes NFTL/INFTL media headers, BBT descriptors, optional writable INFTL BBT blocks, bad-block marks, and generated partitions. Runtime state is global through `doclist`, and per-device through selected floor/chip, current media-header pages, and ECC decoder state. Cleanup unregisters MTD devices, releases mappings/regions, frees RS codecs, and frees allocations.

## Dependencies And Integration Points
Depends on raw NAND, MTD partitions, `doc2000.h` register macros, `inftl.h` media structures, Linux I/O mapping, and Reed-Solomon library support. It integrates with `nand_scan()`, `nand_create_bbt()`, `mtd_device_register()`, legacy NAND ECC callbacks, and the modern `exec_op` instruction model.

## Risks
Probe writes to control registers before full identification and relies on old fixed memory maps. The code mutates NAND/MTD geometry after scan for NFTL virtual erase sizing, making it sensitive to NAND-core internal changes. ECC handling has a `no_ecc_failures` escape hatch that can hide corruption. Multi-floor INFTL is unsupported, Millennium Plus 32 MB is rejected, and OOB free regions are intentionally out of order for compatibility.

## Test Signals
Useful signals are successful probe messages, correct variant/chip-count detection, `nand_scan()` success, NFTL/INFTL media-header discovery, BBT creation, partition registration, ECC corrected/failed counters during page reads, alias-probe rejection of duplicate windows, and unload cleanup without resource leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/diskonchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsl_elbc_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsl_elbc_nand.c

## Purpose
Provides the Freescale Enhanced Local Bus Controller NAND driver using the eLBC Flash Control Machine. It maps one NAND chip-select bank, translates legacy NAND commands into eLBC FCM register sequences, handles controller-buffer data movement, configures hardware ECC when selected, and registers the resulting MTD device with command-line, RedBoot, or device-tree partitions.

## Important APIs, Types, And Functions
`struct fsl_elbc_mtd` stores per-bank NAND chip state, the shared LBC controller, mapped chip buffer, page-size mode, and FMR value. `struct fsl_elbc_fcm_ctrl` embeds `nand_controller` plus shared command-buffer state such as current FCM buffer address, page, read byte count, column, buffer index, command status, MDR, OOB mode, and max bitflips. Key functions include `set_addr()`, `fsl_elbc_run_command()`, `fsl_elbc_cmdfunc()`, `fsl_elbc_read_buf()`, `fsl_elbc_write_buf()`, `fsl_elbc_wait()`, `fsl_elbc_read_page()`, `fsl_elbc_write_page()`, and `fsl_elbc_attach_chip()`.

## Control Flow
`fsl_elbc_nand_probe()` waits for the global LBC controller, resolves the device-tree resource to a bank configured for FCM, allocates shared controller state under `fsl_elbc_nand_mutex`, maps the chip buffer, initializes NAND legacy callbacks, and runs `nand_scan()`. `fsl_elbc_cmdfunc()` handles READ0/READOOB/READID/PARAM/ERASE/SEQIN/PAGEPROG/STATUS/RESET by programming FIR/FCR/FBAR/FPAR/FBCR/MDR registers, calling `fsl_elbc_run_command()`, and serving subsequent byte/buffer reads from the mapped FCM buffer.

## State And Persistence
Runtime state is split between per-bank `priv` and shared `ctrl->nand`; the shared state tracks one active command path and must reflect FCM buffer index and lengths accurately. Persistent flash effects are page programs, erases, hardware-generated ECC bytes, flash-resident BBT descriptors at OOB offset 11, and registered partitions. Remove unregisters the MTD, cleans NAND, unmaps the bank buffer, clears the bank slot, and frees the shared controller when its counter reaches zero.

## Dependencies And Integration Points
Depends on `asm/fsl_lbc.h`, global `fsl_lbc_ctrl_dev`, big-endian LBC register accessors, raw NAND legacy hooks, MTD OOB layout APIs, and MTD partition parsers. The driver uses `nand_controller_ops.attach_chip` to infer or apply ECC settings after NAND identification.

## Risks
The command engine relies on controller-global state, so concurrent bank access would be fragile unless serialized by the NAND core. Only 512-byte and 2048-byte pages are supported. Hardware ECC correction accounting is approximate: LTECCR indicates corrected subpages, but the FIXME notes it only increments corrected once for large-page multi-subpage corrections. Partial/subpage writes intentionally write a full data/OOB buffer path and may surprise callers.

## Test Signals
Probe should log the eLBC bank and address. Register-level tests should cover READID, full-page reads with ECC, OOB-only reads, program/erase status, 512-byte and 2 KiB page modes, partition parser output, and removal after multiple banks. ECC tests should watch `mtd->ecc_stats.corrected`, `failed`, and returned max bitflips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsl_elbc_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsl_ifc_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsl_ifc_nand.c

## Purpose
Implements the Freescale Integrated Flash Controller NAND driver. It binds a NAND chip select configured in the IFC global registers, maps the controller SRAM buffer, programs IFC NAND-machine FIR/FCR sequences for NAND operations, supports 8-bit and 16-bit buses, and configures on-host hardware ECC from CSOR settings.

## Important APIs, Types, And Functions
`struct fsl_ifc_mtd` holds one NAND chip, the shared IFC controller, mapped SRAM base, bank number, and buffer-number mask. `struct fsl_ifc_nand_ctrl` embeds `nand_controller` and stores shared active-command state: buffer address, page, column, index, read length, OOB/ECC-read flags, and max bitflips. Important functions are `set_addr()`, `fsl_ifc_run_command()`, `fsl_ifc_cmdfunc()`, `fsl_ifc_wait()`, `check_erased_page()`, `fsl_ifc_read_page()`, `fsl_ifc_attach_chip()`, `fsl_ifc_sram_init()`, and `fsl_ifc_chip_init()`.

## Control Flow
`fsl_ifc_nand_probe()` resolves the DT resource, matches it to an IFC NAND bank, allocates or reuses shared controller state, maps the bank SRAM, enables NAND-machine events/interrupts, initializes chip callbacks, scans the NAND, and registers MTD partitions. `fsl_ifc_cmdfunc()` translates legacy NAND commands into IFC register programs and starts sequences with `fsl_ifc_run_command()`. Full READ0 operations set `eccread`, read the full page plus OOB, and let `fsl_ifc_run_command()` consume ECCSTAT registers after the interrupt-complete event.

## State And Persistence
Persistent flash state includes page data, OOB, hardware ECC layout, BBT descriptors, and partition data. Runtime state is controller-global through `ifc_nand_ctrl`, including current DMA/SRAM index and ECC status. `fsl_ifc_sram_init()` may temporarily rewrite CSOR/CSOR_EXT for IFC 1.1.0 SRAM initialization, then restores them. Cleanup unregisters MTD, cleans NAND, unmaps SRAM, clears the bank slot, and frees the shared controller when unused.

## Dependencies And Integration Points
Depends on `linux/fsl_ifc.h`, global `fsl_ifc_ctrl_dev`, IFC runtime/global register blocks, raw NAND legacy callbacks, MTD OOB layout APIs, and partition parsers. It uses IFC interrupt state (`ctrl->nand_stat`) and wait queues managed by the IFC core.

## Risks
The source uses a file-global `ifc_nand_ctrl`, so multi-controller assumptions must remain valid. The remove path decrements `counter`, but the probe path shown initializes the shared object without visibly incrementing it, which is a lifecycle risk if multiple chips or removal are exercised. IFC erratum handling disables direct ECCER reporting and reconstructs erased-page behavior in software; regressions can misclassify erased pages as failed. Small-page 8-bit BBT offsets are modified globally.

## Test Signals
Exercise bank matching, SRAM initialization across IFC versions, 8-bit and 16-bit `read_byte` paths, READID/PARAM, full-page ECC reads, erased-page correction, program/erase status, OOB layout/free regions, partition parsing, and module removal. Watch `nand_stat`, ECCSTAT-derived corrected counts, timeout/write-protect logs, and returned max bitflips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsl_ifc_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsl_upm.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsl_upm.c

## Purpose
Provides a NAND controller driver for Freescale LocalBus User-Programmable Machine configurations. The UPM supplies command and address bus waveforms, while normal memory-mapped byte I/O transfers NAND data. The driver offers a compact `exec_op` implementation and uses software Hamming ECC.

## Important APIs, Types, And Functions
`struct fsl_upm_nand` embeds `nand_controller`, `nand_chip`, `struct fsl_upm`, I/O base, UPM command/address pattern offsets, optional ready/busy GPIOs per chip, multi-chip address-line offsets, and current chip selection. `fun_probe()` parses device-tree properties and resources. `func_exec_instr()` executes individual NAND instructions through `fsl_upm_start_pattern()`, `fsl_upm_run_pattern()`, `fsl_upm_end_pattern()`, byte I/O, and ready waits. `fun_exec_op()` selects the target chip and runs the instruction list.

## Control Flow
Probe maps the memory resource, finds the matching UPM by physical address, reads `fsl,upm-addr-offset` and `fsl,upm-cmd-offset`, optionally reads `fsl,upm-addr-line-cs-offsets`, acquires indexed ready/busy GPIOs, initializes the NAND controller, and calls `fun_chip_init()`. Chip initialization binds the first child node as the NAND flash, builds an MTD name from the resource and node, scans `mchip_count` targets, and registers the MTD.

## State And Persistence
The driver stores only runtime controller state: selected multi-chip number, address-line offsets, GPIO descriptors, and UPM pattern metadata. Persistent flash changes are delegated to raw NAND operations: page writes, erases, OOB, and software ECC data. Removal unregisters the MTD and calls `nand_cleanup()`.

## Dependencies And Integration Points
Depends on raw NAND `exec_op`, MTD registration, Freescale localbus UPM helpers from `asm/fsl_lbc.h`, device-tree properties, memory-mapped I/O, and optional GPIO ready/busy handling through `nand_gpio_waitrdy()`.

## Risks
Only the first child node is used as flash description. Multi-chip count is capped below `NAND_MAX_CHIPS`, and chip-select offsets must match board wiring exactly. Data transfers are byte-wide in this driver even if UPM width is wider for command/address encoding. Missing ready/busy GPIO falls back to software waits, which can be slower or less precise.

## Test Signals
Good signals are successful UPM lookup, correct parsing of pattern offsets and multi-chip offsets, READID via UPM command/address patterns, software-ECC page read/write success, GPIO-ready wait behavior versus soft wait fallback, multi-target selection, and clean unregister/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsl_upm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsmc_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsmc_nand.c

## Purpose
Implements the ST/SPEAr Flexible Static Memory Controller NAND driver. It maps separate NAND data, command, address, and FSMC register regions; negotiates NAND timings; supports optional DMA or programmed I/O; configures hardware ECC for older 1-bit and revision-8 8-bit modes; and registers the NAND as an MTD device.

## Important APIs, Types, And Functions
`struct fsmc_nand_data` embeds `nand_controller`, `nand_chip`, AMBA-style PID, bank, clock, DMA channels, completions, timing configuration, and mapped I/O/register addresses. Timing is handled by `fsmc_calc_timings()`, `fsmc_nand_setup()`, and `fsmc_setup_interface()`. Data movement goes through `fsmc_exec_op()`, `fsmc_read_buf()`, `fsmc_write_buf()`, and DMA helpers. ECC uses `fsmc_enable_hwecc()`, `fsmc_read_hwecc_ecc1()`, `fsmc_correct_ecc1()`, `fsmc_read_hwecc_ecc4()`, `fsmc_bch8_correct_data()`, and `fsmc_read_page_hwecc()`.

## Control Flow
`fsmc_nand_probe()` parses DT configuration, maps named resources, enables the clock, reads the AMBA-style ID, initializes optional DMA, applies static DT timings if present, installs controller ops, scans one NAND chip, and registers MTD. `fsmc_exec_op()` handles command/address/data/wait instructions directly through memory-mapped command/address/data windows. Attach chooses ECC behavior based on controller revision and requested ECC engine.

## State And Persistence
Runtime state includes applied timing registers, DMA completions, mapped bank register state, and ECC mode. Persistent flash state is normal NAND content plus OOB/ECC layout. Suspend disables the clock; resume re-enables it, reapplies static timings when present, and resets the NAND. Removal unregisters MTD, cleans NAND, disables the bank, and releases DMA channels.

## Dependencies And Integration Points
Depends on raw NAND controller ops, MTD OOB layout, clock framework, platform named resources, optional DMAengine memcpy channels, OF properties (`bank-width`, `nand-skip-bbtscan`, `timings`, `bank`), and software Hamming correction helpers for the 1-bit hardware syndrome path.

## Risks
`host->mode` defaults to zero in the shown code, so DMA paths are present but not selected unless external/platform data changes it. Revision-8 ECC requires a strict data-then-ECC OOB read sequence and supports only specific OOB sizes. Erased-page handling for BCH8 is heuristic and can hide or over-report errors near the correction limit. Timing math rejects SDR modes with `tRC_min < 30000`, limiting high-speed support.

## Test Signals
Validate resource mapping by name, AMBA ID logging, timing negotiation and DT timing fallback, 8-bit/16-bit bus access, DMA and PIO paths where enabled, ECC1 and ECC4 layouts, BCH8 erased-page behavior, suspend/resume with NAND reset, and MTD read/write/erase with corrected/failed ECC counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsmc_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpio.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpio.c

## Purpose
Implements a generic GPIO-assisted NAND controller. The NAND data bus is memory-mapped, while CLE, ALE, optional chip enable, ready/busy, and write-protect signals are controlled through GPIO descriptors. It supports device-tree and legacy platform data and defaults to software Hamming ECC.

## Important APIs, Types, And Functions
`struct gpiomtd` embeds `nand_controller`, the mapped data window, optional ordering-sync window, `nand_chip`, platform data, and GPIO descriptors for `nce`, `cle`, `ale`, `rdy`, and `nwp`. `gpio_nand_exec_instr()` implements NAND instruction primitives, `gpio_nand_exec_op()` wraps a full operation with chip-enable assertion, `gpio_nand_attach_chip()` fills the default ECC algorithm, and `gpio_nand_probe()` acquires resources and registers the MTD.

## Control Flow
Probe maps the primary I/O resource, optionally maps an I/O sync register, obtains configuration from OF (`bank-width`, `chip-delay`) or platform data, acquires GPIOs, initializes the NAND controller, disables write protection, sets software ECC as the driver default, scans one chip, optionally lets platform data adjust partitions, and registers MTD. Execution toggles CLE/ALE around command/address writes and uses `ioread*_rep()`/`iowrite*_rep()` for data transfers.

## State And Persistence
Runtime state is minimal: GPIO output levels, optional sync-read side effects, configured bus width, and NAND core state. Persistent state is only the NAND flash content and any software ECC/OOB data generated by the NAND core. Remove unregisters MTD, cleans NAND, re-enables write protection, and disables the chip.

## Dependencies And Integration Points
Depends on gpiod consumer APIs, platform resources, optional OF binding `gpio-control-nand`, raw NAND `exec_op`, MTD registration, and platform-data partition hooks. On ARM, `gpio_nand_dosync()` uses a dependent read from `io_sync` to enforce SoC-specific ordering between GPIO changes and NAND I/O.

## Risks
Correctness depends on board wiring and GPIO polarity names. Without `rdy`, waits fall back to software polling. The ARM I/O ordering workaround is platform-specific; missing `io-sync` on hardware that needs it can cause command/data reordering. 16-bit transfers divide lengths by two for word I/O, so odd forced widths must be handled by NAND operation construction.

## Test Signals
Probe should verify all required GPIOs and I/O mapping. Functional tests should cover READID, command/address line toggling, 8-bit and 16-bit data paths, ready/busy GPIO and soft wait fallback, write-protect behavior on probe/remove, platform-data partition adjustment, and software-ECC read/write cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/Makefile

## Purpose
Builds the i.MX/Freescale GPMI NAND controller driver object when `CONFIG_MTD_NAND_GPMI_NAND` is enabled.

## APIs, Flow, And State
The file exposes one Kbuild rule: `obj-$(CONFIG_MTD_NAND_GPMI_NAND) += gpmi-nand.o`. Kbuild turns the configuration symbol into either inclusion in the built-in object list, module object list, or no build. It has no runtime state and no persistence beyond build outputs.

## Dependencies And Integration Points
Depends on the surrounding kernel Kbuild system and the `CONFIG_MTD_NAND_GPMI_NAND` Kconfig symbol. It integrates the `gpmi-nand.c` compilation unit with headers in the same directory (`gpmi-nand.h`, `gpmi-regs.h`, `bch-regs.h`).

## Risks
The rule is intentionally minimal. The main risk is name drift if the C file or Kconfig symbol changes; the driver would silently stop building or fail Kbuild resolution.

## Test Signals
Build tests should confirm that enabling `CONFIG_MTD_NAND_GPMI_NAND=y` or `=m` compiles `gpmi-nand.o` and links/registers the `gpmi-nand` platform driver, while disabling the symbol omits it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/bch-regs.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/bch-regs.h

## Purpose
Defines BCH ECC engine register offsets and bitfield helpers used by the GPMI NAND driver. These macros encode interrupt control, BCH layout selection, flash layout geometry, page size, ECC strength, Galois-field selection, and data chunk sizes for i.MX23/i.MX28 and newer i.MX6-class variants.

## Important APIs, Types, And Functions
The public surface is macro-only: `HW_BCH_CTRL`, `HW_BCH_STATUS0`, `HW_BCH_LAYOUTSELECT`, `HW_BCH_FLASH0LAYOUT0`, `HW_BCH_FLASH0LAYOUT1`, `HW_BCH_VERSION`, IRQ bits, and `BF_BCH_FLASH0LAYOUT*()` field builders. Several helpers consult `GPMI_IS_MX6(x)` to select wider MX6 bit encodings for ECC strength and data-size fields and to enable GF14 selection.

## Control Flow
There is no executable flow. `gpmi-nand.c` computes a `struct bch_geometry`, converts it to `bch_flashlayout0` and `bch_flashlayout1` with these macros, writes the values before BCH DMA operations, and enables/clears BCH completion interrupts through the defined control bits.

## State And Persistence
The header itself stores no state. It describes volatile hardware register state that determines how the BCH block interprets NAND page payload, metadata, ECC chunks, and completion interrupts. Incorrect values affect on-flash ECC layout compatibility.

## Dependencies And Integration Points
Depends on `gpmi-nand.h` type predicates being visible when field-builder macros are used. It is tightly integrated with `gpmi_bch_layout_std()`, `bch_set_geometry()`, `gpmi_nfc_exec_op()`, and the BCH IRQ path.

## Risks
Bitfield helpers have SoC-conditional encodings; using the wrong devdata predicate would program incompatible ECC layout registers. MX6 data-size macros shift values differently than MXS variants. Any change here can break compatibility with existing NAND contents because BCH layout is part of the physical page encoding.

## Test Signals
Unit-level validation can compare generated layout register values for known geometries and SoC types. Hardware signals include successful BCH IRQ completion, correct ECC correction counts, readable pages after reboot, and compatibility with boot ROM expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/bch-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/gpmi-nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/gpmi-nand.c

## Purpose
Implements the Freescale/NXP i.MX GPMI NAND controller driver with BCH hardware ECC and DMA-driven command execution. It supports i.MX23, i.MX28, i.MX6Q, i.MX6SX, i.MX7D, and i.MX8QXP variants, including SoC-specific clocks, timing limits, BCH strengths, boot ROM bad-block-marker behavior, and runtime power management.

## Important APIs, Types, And Functions
The driver state is `struct gpmi_nand_data` from `gpmi-nand.h`: resources, timing state, BCH geometry, DMA transfer slots, buffers, NAND controller/chip, completions, and SoC devdata. Key initialization paths are `acquire_resources()`, `gpmi_init()`, `gpmi_nand_init()`, `gpmi_nand_attach_chip()`, `gpmi_init_last()`, and `bch_set_geometry()`. ECC and layout functions include `legacy_set_geometry()`, `set_geometry_by_ecc_info()`, `set_geometry_for_large_oob()`, `gpmi_bch_layout_std()`, `gpmi_ecc_read_page()`, `gpmi_ecc_write_page()`, raw page/OOB handlers, `gpmi_count_bitflips()`, and `block_mark_swapping()`. NAND operations are executed by `gpmi_nfc_exec_op()` using chained DMA descriptors built by `gpmi_chain_command()`, `gpmi_chain_wait_ready()`, `gpmi_chain_data_read()`, and `gpmi_chain_data_write()`.

## Control Flow
Probe allocates driver state, selects devdata from OF match, maps GPMI/BCH register blocks, requests BCH IRQ and DMA channel, gets clocks, enables runtime PM, initializes GPMI/BCH registers, allocates temporary DMA buffers, and runs `nand_scan()`. Attach computes final BCH geometry, installs ECC callbacks, OOB layout, optional subpage read support, and skips automatic BBT scan so the driver can run boot-specific setup and `nand_create_bbt()`. Each NAND operation resumes the device, applies pending timings, builds a DMA chain from NAND instructions, optionally programs BCH layout registers, waits for DMA and BCH completions, unmaps scatterlists, copies bounce-buffer reads back, clears BCH state, and autosuspends.

## State And Persistence
Runtime state includes mapped registers, clocks, runtime-PM state, DMA mappings, BCH completion status, computed hardware timings, BCH layout registers, auxiliary/status buffers, raw scratch buffer, and `swap_block_mark`. Persistent flash behavior is significant: BCH ECC is stored inline with payload according to computed geometry, ECC-based OOB reads mostly synthesize OOB with the block mark, raw paths extract/interleave ECC bits manually, and MX23 may transcribe bad-block markers and write an `STMP` fingerprint in the boot search area.

## Dependencies And Integration Points
Depends on raw NAND `exec_op`, MTD OOB layout, DMAengine with MXS PIO support, BCH IRQs, clocks, runtime PM, pinctrl PM, OF compatible data, NAND ECC requirement discovery, and register macros from `gpmi-regs.h` and `bch-regs.h`. It integrates with boot ROM assumptions via `nand_boot_init()`, `mx23_boot_init()`, and `gpmi_block_markbad()`.

## Risks
The physical layout is complex and compatibility-sensitive: geometry choices, GF length, metadata size, ECC strength, and block-marker swapping determine whether existing flash remains readable. Raw read/write paths must preserve bit-level interleaving and byte alignment. DMA chains support at most one data instruction and up to `GPMI_MAX_TRANSFERS`; unsupported operation shapes fail. Timeouts dump registers but leave the underlying hardware in an uncertain state until reset. MX23 BCH reset erratum and block-marker transcription are high-risk hardware-specific paths.

## Test Signals
Strong test signals include successful probe on each compatible SoC, timing negotiation for ONFI SDR/EDO modes, DMA and BCH IRQ completion, full-page ECC read/write with corrected/failed counters, raw page/OOB round trips, subpage reads on MX6-class byte-aligned parity, bad-block marking with and without swapping, MX23 transcription stamp handling, suspend/resume reinitialization, and power-management clock enable/disable coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/gpmi-nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/gpmi-nand.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/gpmi-nand.h

## Purpose
Declares the central data structures and SoC predicates for the GPMI NAND driver. It captures hardware resources, BCH geometry, boot ROM geometry, SoC capabilities, timing state, DMA transfer bookkeeping, and top-level driver state shared by `gpmi-nand.c` and register helper headers.

## Important APIs, Types, And Functions
`struct resources` stores mapped GPMI/BCH registers, DMA channel range metadata, and up to five clocks. `struct bch_geometry` describes GF length, ECC strength, BCH page size, metadata, chunk sizes/count, payload, auxiliary/status offsets, bad-block-marker bit position, and metadata ECC flag. `struct boot_rom_geometry` stores ROM search strides. `enum gpmi_type` and `struct gpmi_devdata` distinguish SoC family, max BCH strength, clock names, EDO support, and delay thresholds. `struct gpmi_nfc_hardware_timing`, `struct gpmi_transfer`, and `struct gpmi_nand_data` hold timing, DMA, NAND, BCH, and buffer state. Macros such as `GPMI_IS_MX6()` and `GPMI_IS_MXS()` provide SoC classification.

## Control Flow
The header has no executable flow, but its structures define the state transitions in `gpmi-nand.c`: resource acquisition fills `resources`, geometry setup fills `bch_geometry`, timing negotiation fills `hw`, DMA chain construction uses `transfers`, and probe/attach maintain the embedded NAND controller and chip.

## State And Persistence
All fields are runtime driver state except that `bch_geometry`, `swap_block_mark`, and boot ROM geometry determine persistent on-flash page/OOB interpretation. Changing these definitions or field meanings can break layout compatibility.

## Dependencies And Integration Points
Depends on raw NAND, platform device, DMA mapping, and DMAengine headers. Register helper headers rely on the SoC predicate macros. The C file relies on these structures for all driver subsystems: clocks, PM, DMA, ECC, bad-block handling, and MTD registration.

## Risks
This header centralizes ABI-like internal contracts. Incorrect geometry fields, stale clock limits, or wrong SoC predicates can produce invalid BCH layout registers. `GPMI_MAX_TRANSFERS` and `DMA_CHANS` constrain operation construction and resource assumptions.

## Test Signals
Compile coverage validates structure and macro consistency. Runtime validation comes from matching devdata to OF compatibles, successful geometry computation, correct register field generation from predicates, and DMA operation construction within transfer limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/gpmi-nand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/gpmi-regs.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/gpmi-regs.h

## Purpose
Defines GPMI NAND controller register offsets and bitfield helpers used to build PIO words and timing/control register values. It covers command modes, chip select, address space selection, transfer counts, ECC control, payload/auxiliary pointers, controller mode bits, timing registers, busy timeout, data window, and ready/busy status/debug bits.

## Important APIs, Types, And Functions
The file is macro-only. Important groups are `HW_GPMI_CTRL0*`, `BF_GPMI_CTRL0_*()` command-chain fields, `HW_GPMI_ECCCTRL*` and ECC buffer masks, `HW_GPMI_PAYLOAD`, `HW_GPMI_AUXILIARY`, `HW_GPMI_CTRL1*` mode/timing-delay bits, `HW_GPMI_TIMING0/1`, and SoC-specific ready bits in `HW_GPMI_STAT` and `HW_GPMI_DEBUG`. `BF_GPMI_CTRL0_CS(v, x)` branches on `GPMI_IS_MX23()` because chip-select field width differs.

## Control Flow
No code executes here. `gpmi-nand.c` uses the macros when resetting and configuring GPMI, applying timings, building DMA PIO descriptors for command/address/data/wait operations, enabling BCH encode/decode, and selecting NAND mode, write-protect behavior, BCH mode, and ready/busy routing.

## State And Persistence
The header stores no state, but its constants describe volatile hardware state. Some register settings indirectly affect persistent flash content because ECC encode/decode mode, transfer count, and payload/auxiliary placement define how NAND pages are read or programmed.

## Dependencies And Integration Points
Depends on GPMI SoC predicate macros from `gpmi-nand.h`. Integrated with `gpmi_init()`, `gpmi_nfc_apply_timings()`, `gpmi_chain_command()`, `gpmi_chain_wait_ready()`, `gpmi_chain_data_read()`, and `gpmi_chain_data_write()`.

## Risks
Incorrect field masks can corrupt DMA PIO commands or select the wrong chip, address latch, transfer length, or ECC mode. `BF_GPMI_CTRL0_LOCK_CS()` currently expands to zero despite comments about SoC differences, so any future reliance on lock-CS behavior needs hardware validation. Timing fields are tightly coupled to ONFI timing calculations.

## Test Signals
Generated PIO words should be inspected for representative command/address/data/wait operations on MX23 and MX28-plus variants. Hardware tests should verify ready/busy waits, ECC encode/decode transfers, timing register application, data transfer lengths, and NAND mode/write-protect configuration after reset and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/gpmi-regs.h -->
