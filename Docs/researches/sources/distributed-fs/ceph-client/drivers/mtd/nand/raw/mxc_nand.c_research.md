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
