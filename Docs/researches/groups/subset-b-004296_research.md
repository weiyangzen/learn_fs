# Research: subset-b-004296

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/omap_elm.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/omap_elm.c

Purpose: this file is the TI OMAP Error Location Module driver used by NAND/GPMC BCH users to turn BCH syndrome bytes into bit error locations. It is not a NAND controller itself; it exports `elm_config()` and `elm_decode_bch_error_page()` so another NAND driver can configure BCH4/BCH8/BCH16 geometry and ask the ELM hardware to locate correctable errors.

Important APIs, types, and functions: `struct elm_info` owns the MMIO base, completion, BCH type, ECC step count, syndrome size, and saved suspend registers. `struct elm_registers` snapshots the hardware context. `elm_load_syndrome()` writes per-step syndrome fragments in the layout required by each BCH mode, `elm_start_processing()` marks valid syndrome vectors, `elm_error_correction()` reads `ELM_LOCATION_STATUS` and `ELM_ERROR_LOCATION_*`, and `elm_isr()` completes page processing on `INTR_STATUS_PAGE_VALID`.

Control flow: probe maps the register resource, requests the IRQ, enables runtime PM, initializes the completion, and stores driver data. A client first calls `elm_config()` to validate ECC step size and program `ELM_LOCATION_CONFIG`. For a decode, the driver clears/enables the page interrupt, loads syndrome fragments only for reported-error vectors, starts processing by setting `ELM_SYNDROME_VALID`, waits for IRQ completion, disables the interrupt, copies error counts/locations into `struct elm_errorvec`, clears vector interrupts, and disables page mode.

State and persistence: persistent software state is the configured BCH type, number of ECC steps, syndrome size, and the completion. Hardware state is saved and restored across system sleep under `CONFIG_PM_SLEEP`, including IRQ enable, sysconfig, location config, page control, and BCH-mode-dependent syndrome fragment registers. Runtime PM keeps the hardware clocked while probed and drops it on remove/suspend.

Dependencies and integration points: the exported symbols and `linux/platform_data/elm.h` bind this helper to OMAP NAND/GPMC ECC users. It depends on platform IRQ/MMIO resources, OF compatibles `ti,am3352-elm` and `ti,am64-elm`, and Linux completion/PM-runtime APIs.

Risks: `elm_decode_bch_error_page()` waits without a timeout, so a lost interrupt or wedged ELM can stall its caller. `elm_config()` only rejects ECC step sizes above the module limit and a narrow invalid step-count case, so callers must pass coherent ECC geometry. Syndrome loading uses unaligned word casts from ECC byte buffers and mode-specific byte ordering, making regressions hard to spot without hardware vectors. The global `elm_devices` list is populated but not used here and remove does not delete from it.

Test signals: validate successful probe/runtime PM, client `elm_config()` for BCH4/8/16, decode completion IRQ delivery, correct `error_count`, `error_loc`, and `error_uncorrectable` population, suspend/resume preserving register context, and failure behavior for unsupported ECC size/steps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/omap_elm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/orion_nand.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/orion_nand.c

Purpose: this is the Marvell Orion platform NAND glue driver. It maps a simple memory-mapped NAND window into the raw NAND legacy callbacks, derives command/address latch offsets from platform data or Device Tree, and registers one NAND chip as an MTD device.

Important APIs, types, and functions: `struct orion_nand_info` contains the `nand_controller`, `nand_chip`, and optional clock. `orion_nand_cmd_ctrl()` writes command bytes through CLE/ALE-derived offsets, adjusting for 16-bit bus width. `orion_nand_read_buf()` optimizes buffer reads with 64-bit ARM `ldrd` when available, otherwise uses `readsl()` plus byte tail handling. `orion_nand_attach_chip()` defaults unspecified software ECC to Hamming.

Control flow: probe allocates private state, initializes the controller ops, maps the MMIO resource, parses OF properties `cle`, `ale`, `bank-width`, and `chip-delay` or uses `orion_nand_data`, installs legacy NAND callbacks, enables an optional clock, sets software ECC as the driver default, runs `nand_scan()`, and registers partitions with `mtd_device_register()`. Remove unregisters the MTD device and calls `nand_cleanup()`.

State and persistence: state is limited to the NAND core structures, board latch geometry, bus width flag, optional clock lifetime, and registered MTD partitions. There is no suspend/resume or persistent on-flash policy beyond what the NAND core/partition layer manages.

Dependencies and integration points: the driver depends on raw NAND legacy callback support, MTD partition registration, common clock APIs, OF matching for `marvell,orion-nand`, and legacy `mtd-orion_nand.h` platform data. It assumes one chip select and a board-supplied latch layout.

Risks: OF defaults silently choose CLE bit 0, ALE bit 1, and 8-bit bus width, so incomplete DT can appear to probe but address the wrong latch lines. The optimized ARM read path is architecture-specific and bypasses generic IO helpers. `board` is not explicitly null-checked after legacy platform-data lookup, so non-OF users must provide valid data. Widths above 16 only warn and then continue.

Test signals: probe on OF and platform-data boards, correct ID reads under default and custom CLE/ALE values, 8-bit and 16-bit bus operation, optional clock enable failure handling, partition registration, software Hamming default selection, and clean unregister/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/orion_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/pasemi_nand.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/pasemi_nand.c

Purpose: this driver supports the PA Semi PWRficient on-chip localbus NAND interface. It exposes a single raw NAND chip through legacy command, buffer, and ready callbacks, with the LPC control/status register discovered through a PA Semi PCI device.

Important APIs, types, and functions: `struct pasemi_ddata` stores the `nand_chip`, controller, and LPC control port address. `pasemi_hwcontrol()` sends CLE/ALE cycles using fixed localbus pin offsets and flushes posted writes through `eieio()` plus an LPC control read. `pasemi_device_ready()` checks `LBICTRL_LPCCTL_NR`. `pasemi_read_buf()` and `pasemi_write_buf()` transfer in 0x800-byte chunks with `memcpy_fromio()`/`memcpy_toio()`. `pasemi_attach_chip()` defaults software ECC to Hamming.

Control flow: probe resolves the OF resource, allocates private state, maps the NAND window, locates PCI vendor/device `PCI_VENDOR_ID_PASEMI, 0xa008`, reserves four LPC control IO bytes, installs legacy NAND callbacks, enables flash BBT storage, defaults the ECC engine to software, scans one chip, and registers the MTD device. Failure paths release the IO region, unmap MMIO, and free the state. Remove unregisters MTD, cleans NAND, releases the LPC region, unmaps MMIO, and frees memory.

State and persistence: persistent driver state is the mapped data window, LPC control port, NAND core state, and flash-based bad block table option. There is no PM implementation; hardware state is expected to be valid while bound.

Dependencies and integration points: this file depends on OF address mapping, PCI discovery for the localbus controller, raw NAND legacy callbacks, MTD registration, PA Semi-specific IO ordering, and the compatible `pasemi,localbus-nand`.

Risks: the driver hard-codes CLE/ALE pin offsets and the PCI device ID used to find the ready/control register, so it is tightly coupled to the original platform. It uses non-devm allocation and manual cleanup, making probe error paths important. The same IO address is assigned to read and write; incorrect resource mapping is catastrophic. Flash BBT changes on-media state and should be compatible with existing boot firmware expectations.

Test signals: successful OF resource mapping, PCI LPC controller discovery, request-region conflict handling, NAND ID/read/write cycles, ready polling via `LBICTRL_LPCCTL_NR`, Hamming software ECC default, flash BBT creation/reuse, and remove-path resource release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/pasemi_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/pl35x-nand-controller.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/pl35x-nand-controller.c

Purpose: this is the ARM PL35X/PL353 NAND controller driver used on Xilinx-style SMC systems. It implements raw NAND `exec_op`, SDR timing programming, optional hardware Hamming ECC, OOB layout selection, and one child NAND chip behind the SMC.

Important APIs, types, and functions: `struct pl35x_nandc` owns configuration/data MMIO windows, the NAND controller, selected chip, assigned chip-select bitmap, and temporary ECC buffer. `struct pl35x_nand` stores chip state, CS, address-cycle count, cached ECC config, and timings. Core helpers include `pl35x_nand_exec_op()`, `pl35x_nfc_setup_interface()`, `pl35x_nand_read_page_hwecc()`, `pl35x_nand_write_page_hwecc()`, `pl35x_nand_recover_data_hwecc()`, and `pl35x_nand_attach_chip()`.

Control flow: probe maps the parent AMBA SMC registers plus the NAND data resource, resets controller state by disabling/clearing interrupts, setting 8-bit bus width, bypassing ECC, and programming ECC command triggers, then scans child nodes. Per operation, `pl35x_nfc_exec_op()` selects the chip, applies cached timings/ECC config, and runs a parser that packs command/address/data/wait-ready phases into SMC command/data accesses. Hardware ECC page read/write paths enable APB ECC mode, issue controller-specific page commands, use the special `ECC_LAST` data access on the final transfer, read/write OOB ECC bytes, poll ECC completion, and return to bypass mode.

State and persistence: cached per-chip timing and ECC registers are restored on target selection. On-flash state includes optional flash BBT use and legacy descriptors for on-die ECC. The driver has no explicit PM; hardware register state is initialized at probe and updated during attach/setup.

Dependencies and integration points: it depends on the AMBA parent resource, `memclk` from the parent DT node for timing conversion, raw NAND parser APIs, MTD OOB layout helpers, and compatible `arm,pl353-nand-r2p1`. Hardware ECC supports only 1-bit/512-byte correction and page sizes from 512 bytes through 2 KiB.

Risks: hardware ECC is limited and rejects larger pages or unsupported OOB sizes, so DT/NAND requirements must match. The `ECC_LAST` controller quirk prevents generic ECC helpers and makes last-transfer sizing sensitive. `setup_interface()` obtains `memclk` on each call and has empirical timing adjustments for fast modes. Only one CS is supported. Timeouts on controller interrupt or ECC busy polling indicate stalled hardware.

Test signals: child-node probe with exactly one CS, timing setup across SDR modes, 8/16-bit bus switching for forced byte operations, raw `exec_op` reads/writes, hardware ECC read/write with 16- and 64-byte OOB layouts, ECC correction/failure accounting, BBT behavior, and timeout logs from SMC/ECC polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/pl35x-nand-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/plat_nand.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/plat_nand.c

Purpose: this is a generic platform-data NAND wrapper. It lets board code provide legacy NAND control callbacks, chip options, partition data, and optional probe/remove hooks while the driver supplies resource mapping, controller initialization, optional READY GPIO support, scanning, and MTD registration.

Important APIs, types, and functions: `struct plat_nand_data` contains the controller, chip, mapped IO base, and optional ready GPIO. `plat_nand_gpio_dev_ready()` reads the `ready` GPIO when present. `plat_nand_attach_chip()` selects Hamming when software ECC was requested without an explicit algorithm. `plat_nand_probe()` and `plat_nand_remove()` are the main lifecycle functions.

Control flow: probe requires `platform_nand_data` and at least one chip, allocates state, obtains an optional `ready` GPIO, initializes the raw NAND controller, maps resource 0, copies platform callbacks/options into `chip->legacy`, runs the platform-specific `ctrl.probe()` hook, defaults the ECC engine to software, scans `nr_chips`, and registers partitions through `mtd_device_parse_register()`. On error or remove it calls `nand_cleanup()` and the platform `ctrl.remove()` hook when provided.

State and persistence: driver state is the mapped IO base, optional GPIO descriptor, NAND core state, and platform-provided chip/BBT options. Partition and BBT persistence are delegated to the MTD/NAND core and board-supplied options.

Dependencies and integration points: this driver depends on legacy board-provided `struct platform_nand_data`, GPIO descriptors, raw NAND legacy callbacks, and compatible `gen_nand`. It is a bridge for older non-discoverable NAND wiring rather than a hardware-specific controller.

Risks: correctness depends almost entirely on platform callbacks and options. Missing platform data fails probe even with a matching OF compatible. If no READY GPIO is supplied, readiness behavior falls back to platform code, which may be null depending on board setup. Platform `probe()` side effects must be undone by `remove()` on both normal and error paths.

Test signals: valid and invalid platform data, optional READY GPIO behavior, board callback invocation order, multi-chip scan based on `nr_chips`, partition parsing from platform and probe types, software Hamming defaulting, and cleanup hook execution after scan/register failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/plat_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/qcom_nandc.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/qcom_nandc.c

Purpose: this is the Qualcomm NAND/QPIC controller driver. It supports ADM and BAM DMA-backed register/data transactions, QPIC v1/v2 register differences, BCH/RS ECC configurations, boot-partition codeword layout fixups, custom bad block marker access, and `exec_op` handling for reset/read-id/parameter/status/erase/page commands.

Important APIs, types, and functions: `struct qcom_nand_host` stores per-chip ECC/codeword geometry, register templates, boot partitions, status, and layout flags. It works with `struct qcom_nand_controller` and helper APIs from `nand-qpic-common.h`. Important paths include `update_rw_regs()`, `config_nand_page_read/write()`, `config_nand_cw_read/write()`, `read_page_ecc()`, `parse_read_errors()`, `check_for_erased_page()`, `qcom_nandc_read/write_page*()`, `qcom_nandc_block_bad()`, `qcom_nandc_block_markbad()`, `qcom_nand_attach_chip()`, and the `qcom_*_type_exec()` parser callbacks.

Control flow: probe allocates the controller plus embedded `nand_controller`, selects SoC properties, gets `core` and `aon` clocks, parses ADM CRCI properties when BAM is absent, maps the controller, maps the MMIO resource for DMA, enables clocks, allocates common DMA/register buffers, programs one-time controller setup, then scans child NAND nodes. Attach chooses 512-byte ECC steps, selects 4- or 8-bit ECC from controller capabilities and available OOB, builds raw/ECC config registers, installs page/OOB callbacks, and reallocates BAM transaction state after the final codeword count is known.

State and persistence: state includes DMA descriptors, cached register templates, maximum codewords per page, host list, per-host status, and boot partition table from `qcom,boot-partitions`. On-media persistence is sensitive: OOB layout treats inaccessible BBM/reserved bytes as ECC regions, bad-block operations explicitly read/write the last codeword raw, and optional codeword fixup changes `cw_data`, spare bytes, and ECC config inside boot partitions.

Dependencies and integration points: it integrates with the common QPIC helper layer, DMA mapping, Qualcomm ADM/BAM DMA bindings, clocks, MTD partition parsers `cmdlinepart`, `ofpart`, and `qcomsmem`, and compatibles `qcom,ipq806x-nand`, `qcom,ipq4019-nand`, `qcom,ipq6018-nand`, `qcom,ipq8074-nand`, and `qcom,sdx55-nand`.

Risks: the codeword/OOB layout is intricate and differs between ECC and raw modes; regressions can corrupt BBMs or spare data. Boot-partition fixup changes geometry at page granularity and depends on sorted valid DT ranges. Erased-page handling differs for BCH and RS ECC. Status reads depend on `exec_opwrite` to inspect all codewords after program operations. DMA resource mapping, BAM transaction sizing, and QPIC v2 last-codeword read-location registers are high-risk integration points.

Test signals: probe on ADM, BAM, and QPIC v2 variants; ONFI parameter reads; BCH4/BCH8 and RS4 ECC selection; read/write raw and ECC pages with OOB comparison; erased-page reads with bitflips; bad-block scan/marking on 8- and 16-bit buses; boot partition pages with `qcom,boot-partitions`; partition discovery through `qcomsmem`; and DMA descriptor submission failures/timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/qcom_nandc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/r852.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/r852.c

Purpose: this PCI driver supports Ricoh 85xx xD/SmartMedia card readers as removable raw NAND devices. It handles card detection, engine enable/disable, optional two-stage DMA, hardware ECC, SmartMedia registration, sysfs media type exposure, suspend/resume, and IRQ-driven hotplug.

Important APIs, types, and functions: `struct r852_device` is defined in `r852.h` and stores PCI/MMIO/DMA/card/IRQ state. DMA is managed by `r852_dma_test()`, `r852_dma_enable()`, `r852_dma_done()`, `r852_dma_wait()`, and `r852_do_dma()`. Legacy NAND callbacks include `r852_cmdctl()`, `r852_read_buf()`, `r852_write_buf()`, `r852_read_byte()`, `r852_wait()`, and `r852_ready()`. ECC hooks are `r852_ecc_hwctl()`, `r852_ecc_calculate()`, and `r852_ecc_correct()`. Hotplug flows through `r852_irq()`, `r852_card_detect_work()`, `r852_register_nand_device()`, and `r852_unregister_nand_device()`.

Control flow: PCI probe enables the device, sets a 32-bit DMA mask, requests BARs, allocates the NAND chip and device state, maps BAR0, allocates a coherent 512-byte bounce buffer and temporary sector buffer, creates a freezable workqueue, disables hardware/IRQs, tests DMA capability, registers the shared IRQ, and queues initial card detection. Card work debounces presence, updates media type/readonly state, enables the engine, registers the SmartMedia/xD MTD device, or unregisters and disables the engine on removal.

State and persistence: state is highly dynamic: `card_registered`, `card_detected`, `card_unstable`, `readonly`, `sm`, cached `ctlreg`, DMA stage/state/error, and the workqueue. On-media persistence is through `sm_register_device()` and NAND bad-block/ECC behavior. Module parameters control DMA enablement and debug verbosity.

Dependencies and integration points: it depends on PCI ID `RICOH 0x0852`, raw NAND legacy callbacks, `sm_common.h`, coherent and streaming DMA APIs, completions, spinlocks, workqueues, sysfs device attributes, and system sleep PM callbacks.

Risks: card removal can race with IO, so many callbacks silently return zeros or ignore writes while `card_unstable` is set. DMA is a two-phase internal-buffer plus memory transfer and relies on IRQ sequencing; timeout/error paths must prevent stray writes by resetting DMA address to the bounce buffer. Hardware ECC only reports per-half 256-byte correction for 512-byte sectors. Suspend refuses while CE is asserted. The driver deliberately unregisters/remaps media on hotplug, so cleanup ordering is critical.

Test signals: PCI probe/remove, card insert/remove debounce, xD vs SmartMedia detection, readonly reporting, sysfs `media_type`, PIO and DMA 512-byte transfers, DMA error/timeout paths, ECC correction/failure counters, bad OOB read behavior, suspend/resume with and without registered media, and IRQ masking during removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/r852.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/r852.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/r852.h

Purpose: this header defines the register map, bit fields, ECC status format, DMA constants, private device state, and debug/message helpers for the Ricoh r852 xD/SmartMedia PCI NAND driver.

Important APIs, types, and functions: the main type is `struct r852_device`, which aggregates the NAND controller, MMIO pointer, NAND and PCI backpointers, DMA addresses/completion/bounce buffer, card-detection workqueue state, IRQ spinlock, temporary buffer, and cached control register. Register definitions cover `R852_DATALINE`, `R852_CTL`, `R852_CARD_STA`, card IRQ status/enable, hardware enable, DMA capability/address/settings/IRQ registers, and ECC status bits.

Control flow: the C file uses these constants to switch between command/data/address modes, enable/reset the hardware engine, detect card insertion/removal and readonly state, classify SmartMedia vs xD from DMA capability bits, drive two-stage DMA transfers, and interpret ECC correction results. The `R852_DMA_LEN` constant fixes DMA and ECC operations at 512 bytes.

State and persistence: no independent runtime exists in the header, but the structure layout defines all persistent driver state across callbacks and IRQ/workqueue boundaries. `ctlreg` mirrors the hardware control register so callbacks can change CLE/ALE/CE/ECC/write bits incrementally.

Dependencies and integration points: it includes PCI, completion, workqueue, raw NAND, and spinlock headers. It is private to `r852.c` and also depends conceptually on `sm_common.h` for SmartMedia-specific registration and OOB conventions.

Risks: many register bits are documented as guessed or unknown, so behavior depends on empirical hardware knowledge. The ECC syndrome format is compact and hardware-specific. Because the header exposes raw bit fields without typed accessors, mistakes in `r852.c` can easily combine incompatible modes. The fixed 512-byte DMA length must stay aligned with SmartMedia sector and ECC assumptions.

Test signals: compile coverage with `r852.c`, register bit use matching expected hardware traces, correct DMA capability classification, control-register transitions during NAND commands, card IRQ masks/status values on insert/remove, and ECC syndrome interpretation for clean/correctable/uncorrectable sectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/r852.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/renesas-nand-controller.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/renesas-nand-controller.c

Purpose: this is the Renesas R-Car Gen3 and RZ/N1 NAND controller driver for the Evatronix-derived controller. It implements generic `exec_op`, timing setup, DMA-backed full-page hardware ECC, FIFO-backed subpage ECC, OOB layout, optional IRQ or polling completion, and multi-CS child chip registration.

Important APIs, types, and functions: `struct rnandc` owns controller state, MMIO, clock rate, completion, polling flag, shared DMA buffer, and chip list. `struct rnand_chip` caches per-chip/die CS selection, control/ECC/timing registers, and selected die. `struct rnandc_op` packages command/address/data sequence registers. Key functions include `rnandc_select_target()`, `rnandc_trigger_op()`, `rnandc_wait_end_of_op()`, `rnandc_wait_end_of_io()`, `rnandc_read/write_page_hw_ecc()`, `rnandc_read/write_subpage_hw_ecc()`, `rnandc_exec_op()`, `rnandc_setup_interface()`, and `rnandc_attach_chip()`.

Control flow: probe maps MMIO, enables runtime PM, reads the `eclk` rate for timing calculations, configures IRQ or polling mode, sets a 32-bit DMA mask, clears FIFO, and initializes child NANDs. Attach rejects small-page devices, derives block-size control bits from memory organization, enables subpage reads, chooses/validates ECC, and forces later target reconfiguration. Page read/write uses DMA into a controller-owned buffer with ECC enabled, while subpage operations use FIFO accesses rounded to ECC chunks. Generic operations are translated directly into up to four command phases, two address phases, two delay phases, and one data phase.

State and persistence: per-chip cached timing/control/ECC registers are written on target selection. The shared DMA buffer is resized to the largest registered chip. On-media layout reserves two initial OOB bytes before ECC and free regions. Runtime PM is enabled during probe and released on remove, but there are no custom suspend hooks here.

Dependencies and integration points: the driver uses raw NAND controller ops, Linux DMA mapping, completions, optional IRQs, runtime PM, OF child nodes, and compatibles `renesas,rcar-gen3-nandc` and `renesas,rzn1-nandc`.

Risks: FIFO loops use busy waits with limited internal guarding; stuck FIFO state can spin until the later operation wait. ECC corrected-bit reporting is page-level approximation, not per chunk. Small pages and unsupported eraseblock page counts are rejected. Timing setup requires equal read/write pulse and hold times. Polling fallback changes completion behavior and should be tested separately from IRQ mode.

Test signals: probe with and without IRQ, multiple CS values and duplicate-CS rejection, SDR timing conversion, full-page DMA ECC read/write, subpage read/write, erased-page handling for uncorrectable reports, OOB layout offsets, runtime PM enable/put balance, and timeout logs from operation/IO waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/renesas-nand-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/rockchip-nand-controller.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/rockchip-nand-controller.c

Purpose: this is the Rockchip NAND Flash Controller driver for NFC v6/v8/v9 variants. It provides raw NAND `exec_op`, SDR timing setup, hardware BCH ECC, DMA page transfers, boot-ROM-aware OOB/sys-data shuffling, optional boot-block ECC strength switching, clock/IRQ handling, and child chip registration.

Important APIs, types, and functions: `struct rk_nfc` stores controller config, clocks, MMIO, selected bank, current ECC/timing, completion, chip list, shared page/OOB DMA buffers, and assigned CS bitmap. `struct rk_nfc_nand_chip` stores per-chip CS list, boot block count, boot ECC strength, metadata size, and timing. `struct nfc_cfg` describes variant register offsets, ECC strengths/configs, and BCH status bit layouts. Key functions include `rk_nfc_select_chip()`, `rk_nfc_cmd()`, `rk_nfc_setup_interface()`, `rk_nfc_xfer_start()`, `rk_nfc_write/read_page_hwecc()`, `rk_nfc_write/read_page_raw()`, `rk_nfc_ecc_init()`, and `rk_nfc_attach_chip()`.

Control flow: probe selects match data, maps registers, gets optional `nfc` and required `ahb` clocks, enables clocks, requests an IRQ, and scans child nodes. Child init validates `reg` CS entries, defaults to on-host ECC, sets flash BBT options, installs the Rockchip OOB layout, initializes hardware, scans NAND, reads optional `rockchip,boot-blks` and `rockchip,boot-ecc-strength` for boot media, and registers MTD. Generic operations use simple bank command/address/data registers; page ECC paths use DMA buffers and wait for DMA IRQ plus transfer-ready polling.

State and persistence: per-controller state caches selected bank, current timing, and current ECC strength. OOB persistence is unusual: each 1024-byte data step has 4 bytes of system data before ECC, and the driver rotates these bytes so the MTD-visible BBM/free OOB layout is preserved while reserving boot-ROM page-address metadata. Boot blocks may temporarily switch to a different ECC strength for reads/writes, then restore the normal ECC setting.

Dependencies and integration points: it depends on raw NAND, DMA mapping, clocks, IRQ completions, OF compatibles `rockchip,px30-nfc`, `rockchip,rk2928-nfc`, and `rockchip,rv1108-nfc`, and MTD boot-medium flags/properties.

Risks: 16-bit bus width is unsupported. Raw access to boot blocks with a different boot ECC returns `-EIO` because MTD cannot represent the alternate ECC layout. ECC failure logs but returns success after updating failure stats in the page read path. OOB byte rotation is central to BBM preservation and easy to regress. Shared buffers are manually `kzalloc`/`krealloc` with GFP_DMA and must cover the largest attached chip.

Test signals: probe on v6/v8/v9 configs, clock enable/disable and suspend/resume reset, CS selection and duplicate rejection, generic ID/status operations, ECC strength auto-selection from OOB capacity, DMA read/write timeout handling, boot block ECC switching, OOB/BBM round trips, raw read/write outside boot blocks, and BCH corrected/failure counter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/rockchip-nand-controller.c -->
