# subset-b-004293 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/marvell_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/marvell_nand.c

## Purpose
`marvell_nand.c` is the raw NAND controller driver for Marvell NFC hardware. It supports the older PXA/NFCv1 family and newer Armada/NFCv2 family, including legacy platform data and newer device-tree bindings. The driver bridges the Linux raw NAND controller API to Marvell command registers, timing registers, optional PXA DMA, ready/busy interrupts, and the controller's Hamming or BCH hardware ECC engines.

## Important APIs, Types, and Functions
Core controller state lives in `struct marvell_nfc`, which owns the `nand_controller`, MMIO base, clocks, completion, chip list, capability table, and optional DMA channel/bounce buffer. Per-chip state lives in `struct marvell_nand_chip`, with chip-select descriptors, cached `NDCR`, `NDTR0`, `NDTR1`, address cycle count, selected die, and the chosen ECC layout. `struct marvell_nfc_caps` describes hardware differences such as NFCv2 support, maximum CS/RB pins, legacy binding mode, system-controller setup, DMA capability, and maximum timing mode.

The most important entry points are `marvell_nfc_probe()`, `marvell_nfc_remove()`, `marvell_nand_chips_init()`, `marvell_nand_chip_init()`, `marvell_nand_attach_chip()`, `marvell_nfc_exec_op()`, and `marvell_nfc_setup_interface()`. The command path is built around `marvell_nfc_prepare_cmd()`, `marvell_nfc_send_cmd()`, `marvell_nfc_end_cmd()`, `marvell_nfc_wait_cmdd()`, and `marvell_nfc_wait_op()`. ECC is centered on `marvell_nand_ecc_init()`, `marvell_nand_hw_ecc_controller_init()`, `marvell_nfc_enable_hw_ecc()`, and the Hamming/BCH read-write helpers. `marvell_nfc_layouts[]` is the key table translating page size and requested ECC strength into data, spare, and ECC chunk geometry.

## Control Flow
Probe allocates `struct marvell_nfc`, maps registers, enables clocks, masks/clears interrupts, requests the IRQ, obtains the SoC capability record, initializes system-controller bits when required, optionally initializes PXA DMA for NFCv1, resets the NFC, then scans each NAND child. Chip init parses CS/RB mapping, creates a `nand_chip`, sets legacy or new MTD naming, saves existing timing registers, enables bus-width autodetection, runs `nand_scan()`, and registers the MTD.

Generic raw NAND operations enter through `marvell_nfc_exec_op()`, which selects the active target and runs either the NFCv1 or NFCv2 `nand_op_parser`. NFCv2 supports monolithic accesses plus "naked" command/address/data cycles so large NAND core operations can be split around the controller's 2112-byte transfer limit. The parser builds `struct marvell_nfc_op` values containing NDCB register writes, delays, ready timeouts, and data instruction offsets. Data moves through PIO FIFO helpers, with temporary 8-bit bus forcing when requested by the NAND core. NFCv1 uses specific parser patterns for read-id, erase, status, reset, and wait-ready.

Hardware ECC page I/O bypasses the generic parser with page-oriented helpers. Hamming mode performs one monolithic transfer with optional DMA on NFCv1. BCH mode iterates layout chunks and uses NFCv2 "naked" reads/writes to handle controller chunk limits. Read paths enable ECC, transfer chunks, inspect `NDSR_CORERR`, `NDSR_UNCERR`, and `NDSR_ERRCNT`, then perform raw rereads for erased-page checks when the hardware reports uncorrectable errors. Write paths enable ECC, feed data/spare chunks, wait for `ND_RUN` to clear, wait for ready, then query NAND status.

## State and Persistence Behavior
The driver persists no filesystem state. Runtime state is in MMIO registers, cached per-chip timing/config values, chip lists, completion objects, and optional DMA resources. NAND bad-block table persistence is delegated to raw NAND BBT support when `NAND_BBT_USE_FLASH` is active; the driver installs Marvell-specific BBT descriptors and usually suppresses OOB bad-block marker writes when hardware layout would conflict. Suspend waits for outstanding controller work, disables clocks, and resume re-enables clocks, resets registers, and forces timing registers to be restored on the next target selection.

## Dependencies and Integration Points
This file integrates with the Linux MTD raw NAND core (`nand_controller_ops`, `nand_op_parser`, `nand_scan()`, `mtd_device_register()`), the platform driver model, device tree matching, legacy PXA platform data, clock framework, interrupt completions, optional DMA engine/PXA DMA, syscon/regmap for Armada system-controller enablement, and NAND ECC/BBT/OOB layout APIs. Compatible strings include Armada 8K, AC5, Armada 370, PXA3xx, and deprecated legacy bindings.

## Risks
The largest risks are hardware-layout coupling and error recovery. BCH layouts are fixed and unusual, so wrong ECC strength, OOB size, or bad-block-marker handling can corrupt data or make BBT scans unreliable. NFCv2 naked-operation sequencing depends on `ND_RUN`, FIFO request flags, and command completion bits; missed timeouts can leave the controller wedged. DMA uses a bounce buffer because hardware may transfer rounded lengths, so length and cache-sync mistakes would be data-corrupting. CS1/CS3 selection is explicitly unreliable because of undocumented ADDR5 multiplexing. Suspend/resume must restore timing/config state before further access.

## Test Signals
Useful signals include successful probe across legacy and child-node bindings, multi-CS validation and duplicate-CS rejection, read-id/status/reset/erase operations, raw and ECC page read/write on 512, 2K, 4K, and 8K page devices, Hamming and BCH layouts, erased-page handling after ECC errors, BBT creation with `NAND_BBT_NO_OOB_BBM`, DMA-enabled NFCv1 transfers and PIO fallback, timing setup across supported SDR modes, suspend/resume followed by page I/O, and fault injection for ready timeouts, DMA mapping failures, unsupported ECC requirements, and write-status failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/marvell_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/meson_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/meson_nand.c

## Purpose
`meson_nand.c` implements the Amlogic Meson raw NAND flash controller driver for GXL and AXG SoCs. It provides NAND command execution, DMA-backed data movement, ready/busy interrupt handling with and without a physical RB pin, hardware BCH ECC integration, per-chip timing setup, boot-page short-mode handling, and MTD registration for NAND child nodes.

## Important APIs, Types, and Functions
`struct meson_nfc` is the controller object, holding the raw NAND controller, clocks, MMIO regions, completion, chip list, matched ECC capability data, selected CS/RB parameters, timing cache, command FIFO staging, DMA addresses, and assigned-CS bitmap. `struct meson_nfc_nand_chip` wraps `nand_chip` and records CS lines, per-chip clock/timing values, boot-page metadata, BCH mode, and allocated data/info buffers. `struct meson_nand_ecc`, `struct meson_nfc_data`, `struct meson_nfc_param`, and `struct nand_rw_cmd` describe ECC choices, compatible-specific capabilities, active bus pins, and synthesized read/write command sequences.

The main lifecycle functions are `meson_nfc_probe()`, `meson_nfc_remove()`, `meson_nfc_nand_chips_init()`, `meson_nfc_nand_chip_init()`, `meson_nand_attach_chip()`, and `meson_nand_detach_chip()`. Operation hooks are exposed through `meson_nand_controller_ops`: `meson_nfc_exec_op()`, `meson_nfc_setup_interface()`, attach, and detach. Hardware ECC I/O is implemented by `meson_nfc_read_page_hwecc()`, `meson_nfc_write_page_hwecc()`, raw page variants, OOB variants, `meson_nfc_ecc_correct()`, and `meson_nfc_cmd_access()`.

## Control Flow
Probe allocates the controller, reads match data, initializes the `nand_controller`, maps `nfc` and `emmc` register resources, requests the IRQ, initializes the core/device/divider clocks, sets a 32-bit DMA mask, stores platform data, then scans every NAND child. Each child validates the `reg` CS list, ensures CS lines are unique, detects whether a `nand-rb` property is absent, sets DMA-capable options, calls `nand_scan()`, optionally reads boot-page properties, registers the MTD, and links the chip into the controller list.

Generic operations through `exec_op` first reject data transfers larger than `NFC_CMD_RAW_LEN`, select the chip, then translate NAND op instructions into controller FIFO writes. Command and address instructions emit CLE/ALE words, data instructions use DMA-safe bounce handling when buffers are stack, unaligned, or not DMA-safe, and wait-ready instructions call `meson_nfc_queue_rb()`. RB waiting either uses a physical RB interrupt command or, if there is no RB pin, issues a status-operation based wait that lets hardware watch the IO bus and complete when the status read indicates ready.

Page ECC I/O builds NAND command/address sequences with `meson_nfc_rw_cmd_prepare_and_execute()`, maps the chip's data buffer and per-sector info buffer for DMA, emits a raw or ECC `NFC_CMD_M2N`/`NFC_CMD_N2M` access command, drains the command pipeline, waits for DMA/ECC completion, and unmaps buffers. Hardware ECC stores per-sector metadata in `info_buf`; user OOB bytes are packed into the low bytes of each info entry, while ECC status bits report corrected, erased, or uncorrectable sectors. On uncorrectable reads without scrambling, the driver rereads raw data and uses `nand_check_erased_ecc_chunk()` to distinguish erased pages from real failures.

## State and Persistence Behavior
The driver has no persistent storage beyond NAND media managed by MTD. Runtime state includes clock rates, timing calculations, current CS/RB, boot-page geometry, chip buffers, DMA addresses, and IRQ completions. BBT state is delegated to the NAND core; if flash BBT is requested, attach sets `NAND_BBT_NO_OOB` because OOB bytes are controller-managed. Buffers are allocated during attach and freed on detach. Removal unregisters each MTD, calls `nand_cleanup()`, unlinks chips, and disables clocks.

## Dependencies and Integration Points
The file depends on Linux platform devices, OF child nodes, MMIO helpers, clock framework including a registered divider clock, DMA mapping APIs, IRQ completions, raw NAND controller APIs, NAND ECC capability selection, MTD OOB layout registration, and `object_is_on_stack()`/`virt_addr_valid()` checks for DMA-safe buffers. Compatible data selects GXL or AXG ECC capability tables, with AXG limited to 8-bit BCH on 512 or 1024 byte steps and GXL allowing stronger 1024-byte BCH modes.

## Risks
Important risks include DMA safety and buffer lifetime, since generic NAND op buffers may need bounce copies. `meson_nfc_check_ecc_pages_valid()` polls info-buffer completion without an explicit timeout, relying on preceding command completion and DMA syncs. No-RB-pin behavior is more complex than physical RB waiting and depends on status-command sequencing and optional `nand_exit_status_op()`. ECC/OOB layout leaves only two free user bytes per step, so mismatches with NAND requirements or boot-page short mode can break compatibility. The driver rejects 16-bit bus width and oversize raw operations, so DT or chip data must match these constraints.

## Test Signals
Useful tests include probe on GXL and AXG compatibles, missing and present `nand-rb` handling, duplicate or out-of-range CS rejection, DMA mask failure paths, `exec_op` for read-id/status/parameter-page/program/erase flows, aligned and bounced data buffers, ECC read/write and raw read/write, OOB layout validation, erased-page handling with and without scrambling, boot-medium short mode using `amlogic,boot-pages` and `amlogic,boot-page-step`, timing setup for different SDR modes, clock rate switching per selected chip, and cleanup after partial child initialization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/meson_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/mpc5121_nfc.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/mpc5121_nfc.c

## Purpose
`mpc5121_nfc.c` is the raw NAND controller driver for Freescale MPC5121/MPC5123 NFC hardware. It uses the legacy raw NAND interface callbacks rather than the modern `exec_op` parser, because the hardware exposes page buffers and command/address trigger registers. The driver configures the controller from reset configuration word settings, handles full-page transfers and split spare buffers, supports an ADS5121 board-specific external chip-select path, and registers the NAND as an MTD device.

## Important APIs, Types, and Functions
`struct mpc5121_nfc_prv` owns the `nand_controller`, embedded `nand_chip`, IRQ, MMIO registers, clock, wait queue, current column offset, spare-only flag, optional ADS5121 CPLD chip-select register, and device pointer. Register access helpers `nfc_read()`, `nfc_write()`, `nfc_set()`, and `nfc_clear()` use big-endian 16-bit MMIO. Command helpers include `mpc5121_nfc_send_cmd()`, `mpc5121_nfc_send_addr()`, `mpc5121_nfc_send_prog_page()`, `mpc5121_nfc_send_read_page()`, `mpc5121_nfc_send_read_id()`, and `mpc5121_nfc_send_read_status()`.

The NAND legacy API is wired through `mpc5121_nfc_command()`, `mpc5121_nfc_read_byte()`, `mpc5121_nfc_read_buf()`, `mpc5121_nfc_write_buf()`, `mpc5121_nfc_select_chip()`, and `mpc5121_nfc_dev_ready()`. Attach defaults software ECC to Hamming through `mpc5121_nfc_attach_chip()` when the NAND core requests software ECC without a specified algorithm. Probe and teardown are handled by `mpc5121_nfc_probe()`, `mpc5121_nfc_remove()`, and `mpc5121_nfc_free()`.

## Control Flow
Probe first checks the SoC revision and only supports MPC5121 rev 2 or MPC5123 rev 3. It allocates private state, initializes the NAND controller, binds controller data and flash node, reads hardware NAND page/spare/bus-width configuration from the reset module, maps the IRQ and MMIO range, validates the `chips` property, installs legacy NAND callbacks, optionally initializes ADS5121 external chip-select logic, enables the IPG clock, resets the NFC, unlocks internal RAM and flash blocks, configures big-endian full-page interrupts, sets spare-area size, requests the IRQ, sets a default software ECC engine, scans the requested number of chips, programs pages-per-block bits, then registers the MTD.

`mpc5121_nfc_command()` translates legacy NAND commands into controller command/address/data phases. It normalizes subpage reads and OOB reads into full-page `READ0` operations because the hardware cannot transfer subpages directly. For `SEQIN`, it prereads the target page so a partial update can be staged in the controller buffer before programming. Data access is then performed through `mpc5121_nfc_buf_copy()`, which tracks `prv->column` and routes bytes either to the main RAM buffer or to the controller's segmented spare buffers.

Interrupt completion is handled by `mpc5121_nfc_irq()` and `mpc5121_nfc_done()`. The driver masks/unmasks the NFC interrupt, waits on `irq_waitq` with a timeout, warns on timeout, and clears the completion bit in `NFC_CONFIG2`. Ready/busy is reported as always ready because the controller handles it internally.

## State and Persistence Behavior
No filesystem persistence is present. Runtime state is the current column pointer, spare-only mode, selected chip, mapped registers, wait queue, and controller configuration. NAND BBT persistence is enabled through `NAND_BBT_USE_FLASH`, with the NAND core owning on-flash BBT contents. The driver reads reset-time hardware configuration rather than choosing page size, spare size, or bus width dynamically, and it logs the decoded configuration during probe. Removal unregisters the MTD, cleans up the NAND core, and unmaps the optional ADS5121 CPLD register.

## Dependencies and Integration Points
The file integrates with the platform driver and OF APIs, MPC512x reset module definitions, IRQ and waitqueue APIs, clock framework, MTD raw NAND legacy callbacks, partition/MTD registration, and optional board-specific `fsl,mpc5121ads-cpld` mapping. The compatible string is `fsl,mpc5121-nfc`; the reset module node `fsl,mpc5121-reset` and `chips` property are required for successful initialization.

## Risks
The command path emulates subpage behavior with full-page reads and writes, so partial writes are sensitive to buffer contents and ECC policy. Hardware page/spare/bus width is fixed by reset configuration; incorrect device-tree or boot configuration can make the NAND geometry wrong before scan. Timeout handling logs warnings but some helper paths continue after timeouts, which may leave data validity dependent on later NAND-core checks. ADS5121 chip-select support mutates `csreg` by adding an offset after mapping, so teardown must unmap the adjusted pointer path carefully. Only specific SoC revisions are accepted.

## Test Signals
Useful signals include probe on supported and unsupported revisions, missing reset-node and invalid `chips` property errors, reset timeout handling, read-id/status/read/write/erase flows through legacy callbacks, OOB-only and crossing main-to-spare buffer copies, 512-byte and large-page address cycles, 8-bit and 16-bit reset-config decoding, ADS5121 chip-select behavior, interrupt timeout warnings, software Hamming ECC default selection, pages-per-block configuration for 32/64/128/256 pages, and MTD unregister plus NAND cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/mpc5121_nfc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/mtk_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/mtk_nand.c

## Purpose
`mtk_nand.c` is the raw NAND controller driver for MediaTek NFI hardware on MT2701, MT2712, and MT7622 families. It implements the raw NAND controller API, hardware ECC integration through the separate MediaTek ECC engine, DMA-backed page and subpage transfers, free-OOB/FDM handling, bad-block marker swapping, timing setup, suspend/resume, and MTD registration for NAND child nodes.

## Important APIs, Types, and Functions
`struct mtk_nfc` contains the NAND controller, ECC config, clocks, external ECC engine handle, MMIO base, completion, chip list, shared page buffer, and assigned-CS bitmap. `struct mtk_nfc_nand_chip` wraps a `nand_chip` and stores bad-marker control, FDM geometry, spare-per-sector, and selected CS lines. `struct mtk_nfc_caps` defines SoC-specific spare-size tables, page-format shift, clock divider, maximum sectors, and maximum sector size.

Main lifecycle functions are `mtk_nfc_probe()`, `mtk_nfc_remove()`, `mtk_nfc_nand_chips_init()`, `mtk_nfc_nand_chip_init()`, `mtk_nfc_attach_chip()`, `mtk_nfc_suspend()`, and `mtk_nfc_resume()`. Generic command execution is handled by `mtk_nfc_exec_op()`, `mtk_nfc_exec_instr()`, `mtk_nfc_send_command()`, `mtk_nfc_send_address()`, `mtk_nfc_read_byte()`, and `mtk_nfc_write_byte()`. ECC page paths include `mtk_nfc_write_page_hwecc()`, `mtk_nfc_write_page_raw()`, `mtk_nfc_write_subpage_hwecc()`, `mtk_nfc_read_page_hwecc()`, `mtk_nfc_read_subpage_hwecc()`, and `mtk_nfc_read_page_raw()`.

## Control Flow
Probe initializes the controller, obtains the external ECC engine with `of_mtk_ecc_get()`, reads compatible capabilities, maps registers, enables `nfi_clk` and `pad_clk`, requests the IRQ, sets a 32-bit DMA mask, stores driver data, then initializes NAND children. Each child parses and validates its `reg` CS list, sets DMA/subpage capabilities, defaults ECC engine type to on-host, installs ECC read/write callbacks, sets MTD parent/name and OOB layout, resets the hardware, scans the NAND, registers the MTD, and links the chip.

Generic `exec_op` resets the NFI state, puts the controller in custom command mode, selects the target and runtime page format, then executes command, address, data-in, data-out, and wait-ready instructions one by one. Byte data paths use PIO registers and poll IO-ready. Page and subpage paths use the NAND core high-level helpers for command/address setup, then configure NFI DMA, AHB mode, sector count, and interrupt completion.

ECC attach calculates a supported ECC configuration from DT or NAND requirements. It normalizes step size to 512 or 1024 bytes, chooses a spare-per-sector value from the SoC table, adjusts ECC strength using the external ECC engine, computes FDM register and ECC-reserved bytes, and decides whether the bad-block marker must be swapped between OOB and data stream positions. Write paths pack data plus FDM into the shared buffer, optionally enable ECC encode in NFI mode, DMA the page, wait for completion and address counters, disable ECC, then finish NAND program operation. Read paths DMA sectors, wait for NFI and ECC decode completion, update MTD ECC stats, read FDM registers into `oob_poi`, and swap the bad marker back when needed.

## State and Persistence Behavior
The driver persists no host-side state. Runtime state includes NFI registers, clock state, the external ECC engine handle, completion state, the shared controller buffer, per-chip FDM/bad-marker geometry, and active CS selection. On-flash BBT persistence is handled by the NAND core; when flash BBT is used, the driver sets `NAND_BBT_NO_OOB` because OOB is not protected like page data. Suspend disables clocks; resume re-enables clocks and resets each selected NAND chip because VCC may have been lost.

## Dependencies and Integration Points
The file depends on Linux MTD raw NAND APIs, the MediaTek ECC engine API from `linux/mtd/nand-ecc-mtk.h`, DMA mapping, IRQ completions, clocks, platform and OF child-node parsing, MMIO polling helpers, and MTD OOB layout APIs. Compatible strings map to per-SoC spare-size and sector limits: `mediatek,mt2701-nfc`, `mediatek,mt2712-nfc`, and `mediatek,mt7622-nfc`.

## Risks
The page format is tightly coupled to ECC step size, spare-per-sector tables, and FDM register size; unsupported geometry returns errors during attach or runtime config. The shared `nfc->buffer` is allocated per attach and stored at controller scope, so multi-chip assumptions rely on serialized NAND controller access. Bad-block marker swapping is easy to break because the marker can reside inside the data stream for large pages. DMA timeout paths must clear NFI state and disable ECC correctly to avoid poisoning following operations. The driver rejects 16-bit bus width and only supports on-host hardware ECC.

## Test Signals
Useful signals include probe with and without a ready ECC provider, all compatible capability tables, duplicate/out-of-range CS rejection, ECC strength adjustment from NAND requirements, spare table boundary cases, FDM OOB layout correctness, raw and hardware-ECC page read/write, subpage read and write, erased-page detection via `STA_EMP_PAGE`, bad-block marker swap positions on 512-byte and larger pages, DMA completion timeout behavior, interrupt masking behavior, custom `exec_op` read-id/status flows, suspend/resume reset behavior, and cleanup after child registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/mtk_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/mxc_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/mxc_nand.c

## Purpose
`mxc_nand.c` is the raw NAND controller driver for several Freescale/NXP i.MX NAND Flash Controller revisions: i.MX21, i.MX27/i.MX31, i.MX25/i.MX35, i.MX51, and i.MX53. It adapts multiple register layouts and ECC capabilities to the modern raw NAND `exec_op` interface while also using controller SRAM buffer shuffling for hardware and software ECC modes.

## Important APIs, Types, and Functions
`struct mxc_nand_host` holds the embedded `nand_chip`, MMIO bases, register windows, SRAM main/spare buffers, clock, IRQ, completion, active CS, ECC state, data buffer, and matched `struct mxc_nand_devtype_data`. The devtype table is the main abstraction layer; it supplies per-revision callbacks for preset, page read, command/address send, page transfer, read-id/status, interrupt control, ECC status decoding, OOB layout, chip select, timing setup, and hardware-ECC enablement.

Key functions include `mxcnd_probe()`, `mxcnd_remove()`, `mxcnd_attach_chip()`, `mxcnd_exec_op()`, `mxcnd_do_exec_op()`, `wait_op_done()`, the v1/v2/v3 command/address/page helpers, `preset_v1()`, `preset_v2()`, `preset_v3()`, `mxc_nand_read_page()`, `mxc_nand_write_page_ecc()`, raw/OOB variants, `copy_spare()`, `copy_page_to_sram()`, and `copy_page_from_sram()`. Timing support is implemented for v2 controllers by `mxc_nand_v2_setup_interface()`.

## Control Flow
Probe allocates the host and a temporary data buffer, sets the MTD name and parent, finds a NAND child node when present, gets the clock, reads match data, maps one or two register resources depending on whether the revision needs a separate IP window, computes main/spare/register base pointers, installs the devtype chip-select callback, prepares the completion and IRQ, masks interrupts, requests the IRQ, enables the clock, handles the i.MX21 interrupt-pending quirk, assigns controller ops through the dummy legacy controller, scans one chip or up to four chips on i.MX25, parses/registers partitions, and stores driver data.

`mxcnd_exec_op()` delegates to a NAND op parser with patterns for reads, writes, and command/address/data flows. `mxcnd_do_exec_op()` walks each sub-operation instruction. Commands and addresses are sent via the devtype functions. Data-out copies bytes either directly into main SRAM for on-host hardware ECC or into interleaved main/spare SRAM order for software ECC, then launches an NFC input transfer. Data-in handles read-id and status specially; otherwise it launches a page read and copies from SRAM back into the caller buffer, using a temporary buffer for unaligned lengths.

Hardware ECC attach sets 512-byte ECC steps, revision-specific ECC byte defaults, OOB layouts, read/write callbacks, i.MX-specific BBT descriptors when flash BBT is used, allocates the final page-sized data buffer, reruns the preset after the NAND geometry is known, calculates effective ECC bytes/strength, and caps `used_oobsize` at 218 bytes to avoid copying invalid spare bytes into the controller buffer. Preset functions unlock internal RAM/blocks and configure ECC, page size, OOB size, pages-per-block, address phases, and v3 write-protect/IP registers.

## State and Persistence Behavior
The driver has no filesystem persistence. Runtime state includes clock-enabled status, active CS, completion, ECC statistics collected from hardware registers, cached devtype data, temporary page/OOB buffer, and controller SRAM contents. Flash BBT persistence is owned by the NAND core, with i.MX-specific descriptors used because generic BBT placement conflicts with hardware ECC OOB layout. Select-chip enables the NFC clock on selection and disables it on deselection. Remove unregisters the MTD, calls `nand_cleanup()`, and disables the clock when active.

## Dependencies and Integration Points
The file integrates with platform/OF matching, clock and IRQ frameworks, MTD raw NAND operation parsing, legacy NAND chip-select callbacks, MTD partition parsers (`cmdlinepart`, `RedBoot`, `ofpart`), MMIO access helpers, bitfield macros, and NAND BBT/OOB layout APIs. Compatible strings select the devtype data for `fsl,imx21-nand`, `fsl,imx27-nand`, `fsl,imx25-nand`, `fsl,imx51-nand`, and `fsl,imx53-nand`.

## Risks
The driver must preserve subtle differences between controller revisions, including register widths, interrupt pending quirks, spare buffer sizes, ECC status encoding, page-transfer behavior, and v3 IP/AXI windows. SRAM data order differs between hardware ECC and software ECC paths; mistakes in `copy_page_to_sram()` or `copy_page_from_sram()` would corrupt raw/OOB views. `mxcnd_setup_interface()` blindly calls the devtype callback, so revisions without timing setup set `NAND_KEEP_TIMINGS`. `copy_spare()` caps OOB to avoid corruption, but layouts with large OOB remain sensitive. Timeout paths warn and return errors, but a wedged controller may affect the next operation.

## Test Signals
Useful tests include probe for every compatible revision, i.MX21 IRQ quirk behavior, clock enable/disable on chip select, reset/preset programming after scan, read-id/status/read/write/erase through `exec_op`, hardware ECC and software ECC raw page views, OOB layout checks for v1 and v2/v3, BBT placement with flash BBT, i.MX25 multi-chip scanning, unaligned data-in lengths, 512/2K/4K page geometries, v2 timing acceptance and rejection, interrupt and polling timeout paths, large OOB cap behavior, and remove cleanup with active clock state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/mxc_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/mxic_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/mxic_nand.c

## Purpose
`mxic_nand.c` is the raw NAND controller driver for the Macronix Multi-I/O interface in raw NAND mode. It exposes a simple `exec_op` implementation backed by controller FIFO transfers, manual chip-select control, ready-pin interrupts, clock and phase setup, and single-chip MTD registration.

## Important APIs, Types, and Functions
`struct mxic_nand_ctlr` owns the three clocks (`ps`, `send`, `send_dly`), completion, register base, raw NAND controller, device pointer, and embedded `nand_chip`. Register definitions cover host configuration, interrupt status/enables, TX/RX FIFOs, slave-select control, linear read/write modes, DMA registers, randomizer registers, GPIO, delay lines, and data strobe.

The important functions are `mxic_nfc_probe()`, `mxic_nfc_remove()`, `mxic_nfc_exec_op()`, `mxic_nfc_setup_interface()`, `mxic_nfc_data_xfer()`, `mxic_nfc_wait_ready()`, `mxic_nfc_hw_init()`, `mxic_nfc_set_freq()`, `mxic_nfc_clk_setup()`, `mxic_nfc_clk_enable()`, `mxic_nfc_clk_disable()`, and `mxic_nfc_isr()`. Controller ops include only `exec_op` and `setup_interface`; ECC is left to the NAND core configuration rather than custom page callbacks in this file.

## Control Flow
Probe allocates the controller, gets all clocks, maps registers, binds the first NAND child as the flash node, initializes the raw NAND controller, fetches the IRQ, performs base hardware initialization, requests the IRQ, scans one NAND chip, registers the MTD, and stores driver data. Hardware init sets the controller for raw NAND type, manual chip-select mode, 8-bit I/O, interrupt status enables, ready-pin interrupt signal enable, zeroes ONFI input count and linear-read config, and disables the host controller.

`mxic_nfc_exec_op()` accepts all operations in check-only mode. For real execution it asserts manual CS, initializes the completion, and iterates each NAND op instruction. Command, address, data-in, and data-out instructions program `SS_CTRL(0)` with command/address/data bus width, dummy cycle, byte-count, and read/write direction fields, then use `mxic_nfc_data_xfer()` to move bytes through TXD/RXD FIFO registers. Wait-ready instructions block on the IRQ completion with a one-second timeout. CS is deasserted after the instruction loop.

Timing setup converts SDR `tRC_min` into a target frequency, caps it at 50 MHz, disables clocks, configures send and delayed-send clock rates, writes a fixed input delay code, sets output phase based on frequency, re-enables clocks, and enables EDO strobe mode when `tRC_min` is below 30 ns.

## State and Persistence Behavior
The driver persists no host-side state. Runtime state is the embedded NAND chip, MMIO register configuration, clock rates/phases, completion object, and IRQ state. `nand_scan()` and `mtd_device_register()` create the kernel-visible MTD device; removal unregisters the MTD, calls `nand_cleanup()`, and disables clocks. There is no custom BBT, OOB layout, suspend/resume, DMA, or multi-chip state in this file.

## Dependencies and Integration Points
The driver integrates with the Linux platform driver model, OF match table (`mxic,multi-itfc-v009-nand-controller`), clock framework, MMIO polling helpers, interrupt completions, raw NAND controller operations, and MTD registration. It includes software Hamming ECC headers but does not install custom ECC callbacks; ECC behavior is expected to be selected by NAND core/device-tree policy.

## Risks
The implementation is intentionally simple but has several hardware assumptions. It uses one embedded `nand_chip` and effectively binds child nodes into a single chip, so multi-chip topologies are not represented. `exec_op` returns success for all check-only operations, so unsupported operation shapes would only fail at execution time if the FIFO sequence cannot handle them. FIFO transfer polling has one-second timeouts per byte group and warns if RX FIFO remains non-empty. Clock setup disables clocks before applying rates and phases; failures in the middle can leave clocks off until cleanup or retry.

## Test Signals
Useful signals include probe with all three clocks present, missing-clock errors, IRQ request failure, read-id/status/reset operations through `exec_op`, data-in/data-out transfers with lengths not divisible by four, ready-pin interrupt completion and timeout behavior, setup-interface frequency capping at 50 MHz, EDO strobe enablement for fast timings, MTD registration failure cleanup, and remove path unregistering and disabling clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/mxic_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_amd.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_amd.c

## Purpose
`nand_amd.c` contains manufacturer-specific raw NAND hooks for AMD/Spansion/Cypress NAND devices. It adjusts generic extended-ID decoding for a known Spansion ID layout corner case and sets conservative bad-block-marker scan locations for SLC parts whose datasheets allow markers in multiple pages of an eraseblock.

## Important APIs, Types, and Functions
The exported object is `amd_nand_manuf_ops`, a `struct nand_manufacturer_ops` with `.detect = amd_nand_decode_id` and `.init = amd_nand_init`. `amd_nand_decode_id()` obtains the MTD and NAND memory-organization structures, calls `nand_decode_ext_id()`, then optionally overrides `pages_per_eraseblock` and `mtd->erasesize` for a Spansion/AMD five-byte ID pattern. `amd_nand_init()` checks `nand_is_slc()` and sets `NAND_BBM_FIRSTPAGE`, `NAND_BBM_SECONDPAGE`, and `NAND_BBM_LASTPAGE` when appropriate.

## Control Flow
During manufacturer detection, the raw NAND core calls the detect hook after matching the manufacturer. The hook first runs the generic extended-ID decoder. It then checks for a nonzero fifth ID byte, zero sixth through eighth ID bytes, and a decoded 512-byte page size. This pattern corresponds to Spansion S30ML-P ORNAND style IDs where the erase size implied by the generic NAND ID table may conflict with the extended ID. When matched, the function computes `pages_per_eraseblock` from ID byte 3 and updates the MTD erase size.

During manufacturer initialization, the NAND core calls `amd_nand_init()`. For SLC devices, it broadens bad-block marker policy so the core checks the first, second, and last page of each eraseblock. Non-SLC devices are left unchanged.

## State and Persistence Behavior
The file has no persistent state and allocates no runtime resources. It mutates the in-memory NAND geometry (`nand_memory_organization`) and MTD erase size during detection, and it mutates `chip->options` during initialization. Any on-flash bad-block information remains owned by the NAND core and device media.

## Dependencies and Integration Points
The file integrates directly with raw NAND manufacturer dispatch from `internals.h`, `nand_decode_ext_id()`, `nanddev_get_memorg()`, MTD geometry, SLC detection, and NAND bad-block-marker option flags. It has no platform, OF, IRQ, DMA, clock, or MTD registration logic.

## Risks
The detection override is intentionally narrow, but it depends on ID-byte interpretation and a specific 512-byte page-size condition. If a future AMD/Spansion-compatible device reuses the same byte pattern with different semantics, eraseblock geometry could be misdecoded. The SLC bad-block-marker expansion can increase scan work and may affect devices with unusual marker conventions, but it is conservative for the cited Cypress/Spansion behavior.

## Test Signals
Useful signals include ID decode tests for the Spansion repeating-byte pattern, negative tests where any of bytes 4 through 7 or page size do not match, verification that `mtd->erasesize` follows the recomputed pages-per-eraseblock, SLC initialization setting all three BBM location flags, and non-SLC initialization leaving BBM options untouched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_amd.c -->
