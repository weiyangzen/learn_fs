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
