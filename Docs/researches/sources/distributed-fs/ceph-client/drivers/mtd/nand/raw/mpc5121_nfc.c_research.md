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
