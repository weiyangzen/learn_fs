# Research: subset-b-004297

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sh_flctl.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sh_flctl.c

Purpose: this is the Renesas/SuperH FLCTL raw NAND controller driver. It binds the legacy raw NAND interface to FLCTL command, address, FIFO, DMA, runtime-PM, and optional 4-symbol hardware ECC registers for SH-Mobile style controllers such as `renesas,shmobile-flctl-sh7372`.

Important APIs, types, and functions: the driver centers on `struct sh_flctl` from `include/linux/mtd/sh_flctl.h`, using its MMIO base, FIFO bus address, `nand_chip`, DMA channels, command state, `done_buff`, ECC flags, and PM QoS state. Major helpers include `set_cmd_regs()`, `set_addr()`, FIFO wait/read/write helpers, `flctl_dma_fifo0_transfer()`, `execmd_read_page_sector()`, `execmd_write_page_sector()`, `flctl_cmdfunc()`, `flctl_select_chip()`, `flctl_chip_attach_chip()`, `flctl_probe()`, and `flctl_remove()`. OOB layout helpers define the 4-symbol ECC placement for small and large pages.

Control flow: probe maps the FLCTL register resource, requests the status/error IRQ, derives platform data from DT or board data, initializes legacy NAND callbacks, enables runtime PM, optionally requests SH DMA channels, and scans/registers one NAND target. Raw NAND operations flow through `flctl_cmdfunc()`, which translates legacy commands into FLCTL command-register programming, address setup, FIFO transfer size, translation start, and completion polling. Hardware-ECC page reads use sectorized 512-byte data reads followed by ECC FIFO/status reads and in-place correction in `done_buff`; writes stream data and ECC/OOB sectors through the data and ECC FIFOs. Non-HWECC paths stage data in `done_buff` and use the generic software Hamming setup selected at attach time.

State and persistence: durable software state is mostly per-controller register templates (`flcmncr_base`, `flintdmacr_base`), page geometry/address-count decisions, the staged transfer buffer index, saved SEQIN/ERASE addresses, DMA channels, and a transient PM QoS request while the chip is selected. Persistent media state includes ECC/OOB layout and bad-block marker placement. Runtime PM is acquired around command execution and chip-select register writes; remove releases DMA, unregisters MTD, cleans NAND, and disables runtime PM.

Dependencies and integration points: this file depends on raw NAND legacy callbacks, MTD partition registration, SH DMA filtering/slave IDs, PM runtime/QoS, the FLCTL register definitions in `linux/mtd/sh_flctl.h`, and optional platform data for partitions, clocks/timing register defaults, DMA slave IDs, HWECC, and HOLDEN behavior. DT matching supplies SoC config for SH7372.

Risks: command sequencing is legacy `cmdfunc` based and sensitive to address-count/page-size decisions. FIFO waits use fixed polling loops and only log on timeout, so failures can continue with stale data. DMA failures fall back to PIO but release both channels, changing later behavior. Hardware ECC correction assumes 512-byte sector staging and treats all-0xff sectors specially; incorrect OOB layout or 16-bit address adjustment can corrupt data. PM QoS add failure still sets `qos_request`, which could make cleanup assumptions fragile.

Test signals: successful probe and `nand_scan()`, correct READID over an 8-bit bus even for 16-bit chips, reliable page/OOB reads and writes with and without HWECC, ECC corrected/failed counters changing on injected bitflips, DMA-to-PIO fallback logs without data loss, no FLSTE IRQ errors, runtime PM transitions during repeated chip select/deselect, and correct MTD partition exposure from platform data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sh_flctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sharpsl.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sharpsl.c

Purpose: this is the Sharp SL-C7xx NAND platform driver. It provides board-specific legacy NAND control-line handling, ready polling, hardware Hamming ECC access, bad-block/OOB layout handoff from platform data, and MTD partition registration.

Important APIs, types, and functions: `struct sharpsl_nand` embeds a `nand_controller`, one `nand_chip`, and an MMIO base. `sharpsl_nand_hwcontrol()` maps NAND CLE/ALE/NCE bits into the Sharp FLASHCTL register. `sharpsl_nand_dev_ready()` reads `FLRYBY`, while `sharpsl_nand_enable_hwecc()` and `sharpsl_nand_calculate_ecc()` operate the ECC registers. `sharpsl_attach_chip()` installs 256-byte, 3-byte, 1-bit host ECC using `rawnand_sw_hamming_correct()`. Probe/remove own allocation, mapping, scan, partition registration, and cleanup.

Control flow: probe requires `struct sharpsl_nand_platform_data`, allocates the controller object, maps the single IO resource, initializes the NAND controller ops, links the MTD parent, applies the platform OOB layout and bad-block pattern, enables flash write protect control, installs legacy IO callbacks, scans one chip, names it `sharpsl-nand`, and registers parser/static partitions. Commands then go through the generic legacy NAND core, which calls the driver’s `cmd_ctrl`, `dev_ready`, read/write IO addresses, and ECC callbacks.

State and persistence: driver state is limited to the mapped register window and embedded chip/controller. Hardware state includes FLASHCTL chip enable/CLE/ALE/WP bits and ECC latch/counter registers reset per ECC operation. Persistent media behavior comes from platform-supplied partitions, ECC layout, and bad-block pattern.

Dependencies and integration points: it integrates with the legacy raw NAND API, MTD partition parsers, `linux/mtd/sharpsl.h` platform data, PXA/Sharp board resources, and host-side Hamming correction. It is not DT-oriented and fails probe without platform data.

Risks: the control-line bit mapping is inverted and duplicates CE into two FLASHCTL bits, so regressions are board-specific and easy to miss. ECC calculation returns a nonzero value when `ECCCNTR` is nonzero, which depends on old raw NAND callback expectations. Platform data must provide correct OOB layout and bad-block pattern. The driver uses manual `ioremap()`/`kfree()` rather than devm cleanup.

Test signals: successful platform probe, chip readiness transitions through `FLRYBY`, correct partition table, successful 256-byte ECC calculation/correction, stable bad-block detection with platform pattern, and clean unregister/remove without mapped IO leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sharpsl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sm_common.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sm_common.c

Purpose: this file provides common raw NAND registration support for SmartMedia and xD cards. It supplies their legacy ID tables, OOB layouts, bad-block marking convention, and a single exported helper for host drivers that expose such media as raw NAND.

Important APIs, types, and functions: `sm_register_device()` is the exported entry point. `nand_smartmedia_flash_ids[]` and `nand_xd_flash_ids[]` define legacy IDs, capacity, erase size, ROM, and broken-xD flags. `sm_attach_chip()` sets bad-block marker details, installs `sm_block_markbad()`, and selects the full or small-page OOB layout. The OOB callbacks define ECC positions and LBA/free regions for 512-byte SmartMedia sectors or 256-byte small pages.

Control flow: a caller creates and partially initializes a `nand_chip`/`mtd_info`, then calls `sm_register_device(mtd, smartmedia)`. The function sets `NAND_SKIP_BBTSCAN`, attaches SmartMedia/xD controller ops through the legacy dummy controller, scans one chip against the selected ID table, and registers the MTD device without partitions. During attach, the helper fixes the bad-block marker to OOB offset 5 with 7 valid bits and selects an OOB layout based on `mtd->writesize`.

State and persistence: there is no controller-owned runtime state. Persistent behavior is encoded in the media ID tables, OOB layout, bad-block marker rules, and `NAND_SKIP_BBTSCAN`, leaving card-format metadata such as LBAs visible to higher layers like sm_ftl.

Dependencies and integration points: it depends on raw NAND scan-with-IDs, MTD OOB layout APIs, exported symbol use by SmartMedia/xD host drivers, and the `struct sm_oob` format from `sm_common.h`. The `NAND_BROKEN_XD` flag is propagated through the ID table for larger xD cards.

Risks: the small-page layout is explicitly not fully SmartMedia-compliant for 256-byte devices, except that it preserves bad-block markers. `sm_block_markbad()` assumes erase-block-aligned offsets and requires a full 16-byte OOB write. Skipping BBT scan avoids generic BBT behavior and relies on the format’s own marker semantics. Unsupported write sizes return `-ENODEV`.

Test signals: successful detection of known SmartMedia/xD IDs, correct OOB ECC/free region reporting for 256- and 512-byte writes, bad-block marking writing `block_status = 0x0f`, preservation of LBA metadata for sm_ftl, and cleanup on `mtd_device_register()` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sm_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sm_common.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sm_common.h

Purpose: this header defines the shared SmartMedia/xD OOB structure, format constants, registration prototype, and small validity helpers used by SmartMedia/xD NAND support.

Important APIs, types, and functions: `struct sm_oob` is the packed 16-byte spare-area format with reserved bytes, data status, block status, two LBA copies, and two ECC fields. Constants include `SM_SECTOR_SIZE`, `SM_OOB_SIZE`, `SM_MAX_ZONE_SIZE`, `SM_SMALL_PAGE`, and `SM_SMALL_OOB_SIZE`. `sm_register_device()` is declared for host drivers. Inline helpers `sm_sector_valid()`, `sm_block_valid()`, and `sm_block_erased()` classify spare-area status bytes and erased OOB patterns.

Control flow: the header itself has no execution path, but `sm_common.c` writes `struct sm_oob` instances when marking bad blocks and host/FTL code can use the inline helpers while scanning card metadata. The validity helpers use Hamming weight thresholds rather than exact-byte comparisons for status fields, matching SmartMedia’s bit-tolerant status encoding.

State and persistence: all state described here is on-media spare-area metadata. The packed struct fixes the physical layout that persists in NAND OOB. `sm_block_erased()` treats an all-0xff 16-byte OOB as erased.

Dependencies and integration points: it includes Linux bit operations and MTD core declarations. It is paired with `sm_common.c` and any SmartMedia/xD translation layer that needs to interpret LBA/status fields.

Risks: the `sm_block_erased()` helper compares the whole packed OOB structure to a static 16-byte erased pattern; structure size/layout must remain exactly 16 bytes. `hweight16()` is used on 8-bit fields after integer promotion, so callers must pass valid `struct sm_oob` contents. Any change to this header affects on-media format interpretation.

Test signals: compile-time packed struct size stability, correct valid/invalid threshold behavior for status bytes, erased OOB detection for all-0xff data, and consistency with the OOB layout offsets implemented in `sm_common.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sm_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/socrates_nand.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/socrates_nand.c

Purpose: this is the ABB/Emcraft Socrates board NAND driver for an FPGA-backed NAND access register. It adapts raw NAND legacy callbacks to a big-endian FPGA command/data/status register and defaults to software Hamming ECC.

Important APIs, types, and functions: `struct socrates_nand_host` embeds a `nand_controller`, a `nand_chip`, the FPGA MMIO base, and device pointer. `socrates_nand_cmd_ctrl()` emits command/address cycles through `FPGA_NAND_CMD_COMMAND` or `FPGA_NAND_CMD_ADDR`; `socrates_nand_read_buf()`, `write_buf()`, and `read_byte()` perform byte transfers through the register’s data field; `socrates_nand_device_ready()` reads `FPGA_NAND_BUSY`. `socrates_attach_chip()` selects soft Hamming when the core left the algorithm unknown.

Control flow: probe devm-allocates the host, maps the first OF resource with `of_iomap()`, initializes the NAND controller, links controller data and flash node, installs legacy callbacks, sets a conservative 20 us chip delay, defaults ECC engine type to software, scans one chip, and registers the MTD. Command and data paths are synchronous register writes/reads with no DMA or IRQ handling.

State and persistence: runtime state is the mapped FPGA register and embedded NAND objects. Persistent media behavior is generic raw NAND plus the selected software ECC. Remove unregisters MTD, calls `nand_cleanup()`, and unmaps the FPGA register.

Dependencies and integration points: it depends on OF matching for `abb,socrates-nand`, raw NAND legacy callbacks, MTD registration, big-endian IO accessors, and the FPGA register protocol defining command type, data shift, enable, and busy bits.

Risks: the driver writes one byte per 32-bit big-endian register access, so bus ordering and FPGA semantics are critical. There is no explicit timeout beyond generic NAND waits and fixed chip delay. Probe uses devm memory but manual `of_iomap()`/`iounmap()`. The comment admits the real command delay is unknown, so timing margins require hardware validation.

Test signals: successful DT probe, READID through command/address/data register paths, ready/busy polarity correctness, stable software-Hamming reads/writes, MTD registration, and no timeout or corrupted-byte symptoms under repeated page transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/socrates_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/stm32_fmc2_nand.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/stm32_fmc2_nand.c

Purpose: this is the STMicroelectronics STM32 FMC2 NAND Flash Controller driver. It supports STM32MP1/MP25 FMC2 NFC instances with memory-mapped command/address/data windows, regmap-controlled FMC2 registers, host Hamming/BCH ECC, optional DMA sequencer mode, multiple chip-enable mappings, write-protect GPIO, timing calculation, and system PM.

Important APIs, types, and functions: `struct stm32_fmc2_nfc` holds the `nand_controller`, one NAND device, regmap, IO windows, physical addresses, DMA channels/SG tables/ECC buffer, completions, chip-select state, and SoC data. `struct stm32_fmc2_nand` stores the `nand_chip`, WP GPIO, timings, and assigned chip selects. Key paths are `stm32_fmc2_nfc_setup()`, `stm32_fmc2_nfc_select_chip()`, ECC helpers for Hamming/BCH calculate/correct/decode, polling read/write callbacks, sequencer DMA callbacks, `stm32_fmc2_nfc_exec_op()`, timing setup, DMA setup, attach, DT parsing, probe/remove, and suspend/resume.

Control flow: probe selects compatible data, validates whether the NFC is a child of the shared FMC2 EBI device or a standalone controller, parses exactly one NAND child and its `reg` chip-select list, maps data/cmd/addr windows per CS, gets IRQ/clock/reset/regmap, optionally configures DMA channels and SG tables, initializes the FMC2 registers, disables WP, scans the NAND, and registers MTD. Generic operations use `exec_op()` for command/address/data/wait instructions. Page callbacks are chosen at attach time: with all DMA channels available, sequencer mode configures CSQ registers and runs page DMA plus ECC-status DMA; otherwise polling mode uses column operations and explicit ECC calculate/correct callbacks.

State and persistence: persistent driver state includes chip-select assignments, current selected CS, calculated timings, DMA availability, ECC strength/bytes, OOB layout, WP GPIO state, and regmap-backed controller configuration. Suspend disables the clock, enables WP, and selects sleep pinctrl; resume restores pinctrl/clock, reinitializes FMC2, disables WP, and resets each assigned chip.

Dependencies and integration points: it integrates with raw NAND `exec_op`, MTD OOB layouts, DMAengine, regmap/syscon, reset controls, GPIO descriptors, clocks, pinctrl PM states, OF resources, and the related STM32 FMC2 EBI parent binding. Compatibles include `st,stm32mp15-fmc2`, `st,stm32mp1-fmc2-nfc`, and `st,stm32mp25-fmc2-nfc`.

Risks: DMA sequencer mode depends on three channels and multiple completions; missing DMA falls back to polling but changes callback behavior. BCH IRQ completion and sequencer IRQ completion share one completion and `irq_state`, so ordering must remain exact. OOB layout reserves the first two bad-block marker bytes and packs all ECC after them. Timing calculations clamp fields and support only SDR modes up to 3. Parent/child FMC2 device selection is strict and can reject misdescribed DTs. Resume resets chips after reinitialization, which can expose board timing/WP mistakes.

Test signals: probe on standalone and EBI-child bindings, CS mapping across MP1 and MP25 max-CS variants, Hamming/BCH4/BCH8 ECC selection and byte counts, DMA sequencer reads/writes with ECC status correction, polling fallback when DMA is absent, erased-page ECC handling, OOB free/ECC layout, WP GPIO transitions, timing setup for SDR modes 0-3, suspend/resume with chip reset, and timeout-free IRQ completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/stm32_fmc2_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sunxi_nand.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sunxi_nand.c

Purpose: this is the Allwinner/Sunxi raw NAND controller driver for A10, A23/A33, and H616-class NFC variants. It handles register-level command execution, SRAM-buffered PIO, normal or MBUS DMA, hardware ECC, randomizer/scrambling, variable OOB user-data regions, timing setup, multiple child chips and chip-select/RB mappings, and per-SoC capability differences.

Important APIs, types, and functions: `struct sunxi_nfc` stores controller state, clocks, reset, assigned chip-select mask, chip list, completion, DMA channel, and `sunxi_nfc_caps`. `struct sunxi_nand_chip` embeds `nand_chip`, timing registers, selected CS/RB lines, ECC register template, and optional per-step user-data lengths. Major paths include interrupt/wait/reset helpers, DMA prepare/cleanup, `sunxi_nfc_select_chip()`, randomizer state/config/read/write helpers, hardware ECC chunk/page/subpage read/write paths, timing setup, OOB layout callbacks, ECC initialization/max-strength selection, operation parser execution, chip initialization/cleanup, and probe/remove.

Control flow: probe maps registers, gets IRQ, clocks, optional reset, resets the NFC, requests DMA unless the SoC uses internal MBUS DMA, and initializes each child NAND node. Each chip parses `reg` CS lines and optional `allwinner,rb`, sets default on-host ECC, scans, and registers an MTD. Generic non-page operations are packed by `nand_op_parser_exec_op()` into one or two command bytes, up to eight address cycles, optional SRAM data transfer, and optional ready wait. Page operations use custom hardware-ECC callbacks that move data by PIO chunks or DMA, program ECC/randomizer/user-data registers, check pattern and ECC status bits, reread raw data for erased-page classification, update MTD ECC stats, and read/write extra OOB as needed.

State and persistence: persistent driver state includes SoC capability tables, current controller clock rate, per-chip timing values, CS/RB mappings, selected ECC strength/size/bytes, per-step user-data lengths on H6/H616, and the `NAND_NEED_SCRAMBLING` decision from core NAND. Media persistence is tightly coupled to OOB packing: each ECC step has user data followed by ECC bytes, with the first user-data bytes carrying bad-block markers.

Dependencies and integration points: it depends on raw NAND op parsers, MTD OOB APIs, DMAengine, clocks, resets, OF child nodes, and Allwinner-specific register layouts. Compatibility data selects register offsets, ECC masks, randomizer masks, DMA mode, available ECC strengths, user-data length tables, and SRAM size.

Risks: OOB layout differs significantly between A10/A23 fixed user-data and H616 variable user-data registers. Randomizer state must match page and ECC-step seeds, including explicit bad-block marker randomization/de-randomization. DMA fast paths still use PIO for some OOB retrieval and fall back to PIO on errors. ECC-maximize behavior has a legacy compatibility mode that intentionally preserves older strength choices. Timing setup has several unsupported timing exits and EDO-mode heuristics. Multi-CS assignment must avoid duplicate CS lines.

Test signals: probe for all three compatibles, command parser behavior with and without RB pins, timing setup at supported SDR modes, hardware ECC strength negotiation and OOB layout, reads/writes with `NAND_NEED_SCRAMBLING`, erased-page bitflip handling, DMA and MBUS DMA page transfers with PIO fallback, H616 variable user-data lengths, multi-chip child initialization, and correct reset/clock cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sunxi_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/technologic-nand-controller.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/technologic-nand-controller.c

Purpose: this is the Technologic Systems TS72xx NAND controller driver. It exposes a memory-mapped NAND bus where address-line aliases select control and busy views, and implements modern `exec_op` callbacks for command, address, data, and wait-ready operations.

Important APIs, types, and functions: `struct ts72xx_nand_data` embeds a `nand_controller`, one `nand_chip`, and three MMIO pointers: base data, control alias, and busy alias. `ts72xx_nand_attach_chip()` rejects on-host ECC and defaults software ECC to Hamming. `ts72xx_nand_ctrl()` updates CLE/ALE/NCE bits. `ts72xx_nand_exec_instr()` handles individual NAND operation instructions, and `ts72xx_nand_exec_op()` runs them in order.

Control flow: probe allocates data, initializes controller ops, maps the base resource, derives control/busy aliases by adding fixed address-line offsets, requires exactly one child NAND node, sets the flash node and MTD parent, defaults ECC to software, scans one chip, and registers MTD with parser support. Runtime operations are straightforward: command and address instructions assert the relevant control bits around byte writes, data instructions use `ioread8_rep()`/`iowrite8_rep()`, and WAITRDY polls the busy alias for bit 5.

State and persistence: driver runtime state is limited to MMIO aliases and embedded NAND objects. Persistent media state comes from the child node, generic MTD partition parsing, and software Hamming ECC selection. Remove unregisters MTD, cleans NAND, and puts the firmware node handle.

Dependencies and integration points: it uses raw NAND `exec_op`, `linux/mtd/platnand.h`, firmware child nodes, platform MMIO resources, `readb_poll_timeout()`, and the `technologic,ts7200-nand` compatible.

Risks: the address-line alias scheme assumes the platform maps enough address space for `BIT(22)` and `BIT(23)` offsets from the base mapping. The driver claims it expects exactly one child but only fetches the first child, so extra children are not explicitly rejected. `fwnode_handle_put()` in remove uses `dev_fwnode(&pdev->dev)` rather than the child handle acquired in probe, which is a lifetime area to verify. Unsupported on-host ECC returns `-EINVAL`.

Test signals: successful DT child parsing, command/address strobes on the alias control address, busy polling bit 5, byte-stream reads and writes, software Hamming correction, partition parser registration, and remove-path handle cleanup under probe failure and normal unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/technologic-nand-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/tegra_nand.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/tegra_nand.c

Purpose: this is the NVIDIA Tegra20 NAND controller driver. It provides parsed command execution, DMA page transfers, hardware RS or BCH ECC, timing setup from SDR timings, runtime clock PM, optional write-protect GPIO, and a single-child/single-CS raw NAND integration.

Important APIs, types, and functions: `struct tegra_nand_controller` stores the controller, MMIO base, IRQ, clock, command/DMA completions, last-read-error flag, current CS, and chip pointer. `struct tegra_nand_chip` embeds the NAND chip, WP GPIO, ECC OOB region, config templates, BCH config, and CS. Key functions are `tegra_nand_irq()`, `tegra_nand_cmd()`, `tegra_nand_page_xfer()`, raw and HWECC page/OOB callbacks, `tegra_nand_setup_timing()`, ECC strength selection helpers, `tegra_nand_attach_chip()`, child parsing, probe/remove, and runtime PM callbacks.

Control flow: probe maps registers, gets reset and clock, initializes Tegra OPP support, enables runtime PM/clock, resets hardware, programs status/IRQ defaults, requests IRQ, clears DMA done status, parses exactly one child NAND node with one CS, scans, and registers MTD. Small command operations use a NAND op parser to program command/address registers and optionally exchange up to four bytes through `RESP`. Page/OOB operations use `tegra_nand_page_xfer()`, which maps data and/or OOB buffers for DMA, programs DMA pointers and command bits, waits for command and DMA completions, and aborts/dumps registers on timeout. Hardware ECC wraps page DMA with ECC config and interprets decoder status.

State and persistence: persistent runtime state includes controller config templates for raw vs ECC mode, BCH config, current CS, selected ECC algorithm/strength, OOB ECC region, and `last_read_error` latched from IRQ status. Runtime PM only gates the clock; the driver keeps the device resumed while bound.

Dependencies and integration points: it depends on raw NAND op parsers, DMA mapping, Tegra common OPP setup, reset and clock frameworks, GPIO descriptors, MTD OOB layouts, runtime PM, and the `nvidia,tegra20-nand` compatible.

Risks: only one NAND chip and one CS are supported. ECC requires 512-byte steps; BCH is limited to 2K/4K pages, while RS/BCH boot-medium strength choices are restricted. Corrected-bit statistics are overestimated because hardware reports only the maximum correction count per page and corrected-sector bitmap. Erased-page handling rereads OOB when all sectors fail. DMA timeouts trigger a controller abort and IRQ disable/enable cycle. The OOB layout exposes no free regions.

Test signals: probe with a single child CS, OPP/runtime PM clock enable, small op parser READID/status behavior, DMA page/OOB transfers, command/DMA timeout register dumps absent during stress, RS and BCH ECC strength selection, erased-page false-failure handling, corrected/failed ECC stat updates, timing register programming, and runtime suspend/resume clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/tegra_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/txx9ndfmc.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/txx9ndfmc.c

Purpose: this is the Toshiba TXx9 NDFMC platform driver. It supports up to four platform-described NAND channels, legacy raw NAND callbacks, controller timing setup from GBus clock parameters, optional 16-bit channels, simple hardware Hamming ECC, and resume-time controller reinitialization.

Important APIs, types, and functions: `struct txx9ndfmc_drvdata` stores MTD pointers for up to four devices, MMIO base, hold/strobe timing fields, and a shared `nand_controller`. `struct txx9ndfmc_priv` stores a platform device, chip, CS number, and MTD name. Core functions include register access helpers, `txx9ndfmc_cmd_ctrl()`, byte/buffer IO callbacks, ready polling, HWECC enable/calculate/correct callbacks, `txx9ndfmc_initialize()`, `txx9ndfmc_attach_chip()`, probe/remove, and PM resume.

Control flow: probe consumes `struct txx9ndfmc_platform_data`, maps registers, converts hold and strobe pulse widths from nanoseconds to GBus cycles, initializes the controller, resets/configures NDFMC, and then iterates over the channel mask. Each enabled channel gets an allocated private object, legacy NAND callbacks, optional channel-select name, optional 16-bit flag, scan, MTD naming, registration, and storage in `drvdata->mtds[]`. Commands update CLE/ALE/CE and optional CS bits in the mode register, then write command bytes to the data register. Buffer writes set `WE`, stream bytes as raw 32-bit writes, and restore mode.

State and persistence: shared state includes timing register values, base mapping, and the shared controller. Per-channel state includes chip object, CS selection, MTD name, and channel presence in `mtds[]`. Resume reinitializes controller registers if drvdata exists. Persistent media behavior includes hardware ECC layout chosen by generic NAND core and channel-specific 16-bit bus configuration.

Dependencies and integration points: it uses raw NAND legacy callbacks, MTD registration, `linux/platform_data/txx9/ndfmc.h`, platform channel masks/timing flags, and optional PM resume. There is no DT parsing in this file.

Risks: probe does not fail if an enabled channel allocation, scan, or registration fails; it continues and can return success with fewer MTDs than requested. Platform data is assumed valid before dereferencing. Timing fields are clamped to 4-bit values, so bad GBus clock data can silently produce marginal timings. HWECC reads ECC bytes in a controller-specific byte order and corrects in 256-byte chunks. Dummy-write latch behavior is platform-flag dependent.

Test signals: controller reset completion, printed HOLD/SPW values matching board timing, every channel in `ch_mask` appearing as an MTD, CS selection when multiple channels are active, 16-bit channel READID/data transfer, HWECC correction over 256- and 512-byte page chunks, dummy-write platforms, and resume restoring NDFSPR/NDFMCR state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/txx9ndfmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/vf610_nfc.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/vf610_nfc.c

Purpose: this is the Freescale/NXP VF610 NFC raw NAND driver, also documenting MPC5125/MCF54418/Kinetis limitations. It implements SRAM-buffered command execution, page-size hardware ECC for 2K pages, endian-aware SRAM access, single-child chip-select support, IRQ-completion command execution, and sleep PM clock restore.

Important APIs, types, and functions: `struct vf610_nfc` embeds `nand_controller`, `nand_chip`, device, MMIO base, command completion, SoC variant, clock, `data_access` endian flag, and ECC mode. Core helpers include register field accessors, SRAM read/write wrappers, `vf610_nfc_done()`, `vf610_nfc_cmd()`, `vf610_nfc_exec_op()`, `vf610_nfc_correct_data()`, hardware-ECC page callbacks, raw page/OOB wrappers, controller preinit/init, attach, probe/remove, and PM suspend/resume.

Control flow: probe maps registers, enables the clock, reads the OF match variant, finds exactly one `fsl,vf610-nfc-nandcs` child, initializes completion/IRQ, preinitializes controller config, sets controller ops, scans one chip, stores drvdata, and registers MTD. Generic operations are constrained by the NAND op parser into the hardware’s required order: optional command, address, data-out, second command, wait-ready, and data-in. `vf610_nfc_cmd()` stages write data into internal SRAM, programs command/address/code fields, starts the controller, and copies read data back from SRAM. Hardware-ECC page callbacks bypass the generic op path to transfer full data+OOB with ECC mode enabled and then inspect ECC status stored in SRAM.

State and persistence: controller state includes FLASH_CONFIG bits, ECC mode, bus width, ECC status SRAM address, and the `data_access` flag that decides whether SRAM byte-swapping is applied for raw command data. Persistent media behavior is limited to large-page OOB layout and 24- or 32-bit page-sized ECC. Suspend disables the clock; resume reenables it and reruns controller preinit/init.

Dependencies and integration points: it uses raw NAND op parsers, MTD large-page OOB layout helpers, IRQ completions, clocks, OF child nodes, platform resources, and `fsl,vf610-nfc`. It explicitly supports only one NAND chip child in this implementation.

Risks: the driver’s own limitations are substantial: DMA and pipelining are unused, pages over 2K are unsupported, hardware ECC supports only 2K pages with at least 64 OOB bytes, and only 24/32-bit strengths are implemented. Endian behavior is intentionally historical: page accesses avoid byte swapping while non-page/raw access may swap on little-endian systems. ECC correction treats failed pages as erased if bit counts are below half-strength, which is conservative but hardware-specific. Command completion timeout only warns before clearing status.

Test signals: successful child-node detection, READID/status through `exec_op`, 8-bit forced accesses on 16-bit chips, 2K page hardware ECC read/write with 24- and 32-bit strengths, raw page/OOB paths preserving endian expectations, erased-page ECC classification, unsupported geometry rejection, IRQ completion without BUSY timeouts, and suspend/resume restoring FLASH_CONFIG/ECC status settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/vf610_nfc.c -->
