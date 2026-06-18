## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/txx9ndfmc.c

Purpose: this is the Toshiba TXx9 NDFMC platform driver. It supports up to four platform-described NAND channels, legacy raw NAND callbacks, controller timing setup from GBus clock parameters, optional 16-bit channels, simple hardware Hamming ECC, and resume-time controller reinitialization.

Important APIs, types, and functions: `struct txx9ndfmc_drvdata` stores MTD pointers for up to four devices, MMIO base, hold/strobe timing fields, and a shared `nand_controller`. `struct txx9ndfmc_priv` stores a platform device, chip, CS number, and MTD name. Core functions include register access helpers, `txx9ndfmc_cmd_ctrl()`, byte/buffer IO callbacks, ready polling, HWECC enable/calculate/correct callbacks, `txx9ndfmc_initialize()`, `txx9ndfmc_attach_chip()`, probe/remove, and PM resume.

Control flow: probe consumes `struct txx9ndfmc_platform_data`, maps registers, converts hold and strobe pulse widths from nanoseconds to GBus cycles, initializes the controller, resets/configures NDFMC, and then iterates over the channel mask. Each enabled channel gets an allocated private object, legacy NAND callbacks, optional channel-select name, optional 16-bit flag, scan, MTD naming, registration, and storage in `drvdata->mtds[]`. Commands update CLE/ALE/CE and optional CS bits in the mode register, then write command bytes to the data register. Buffer writes set `WE`, stream bytes as raw 32-bit writes, and restore mode.

State and persistence: shared state includes timing register values, base mapping, and the shared controller. Per-channel state includes chip object, CS selection, MTD name, and channel presence in `mtds[]`. Resume reinitializes controller registers if drvdata exists. Persistent media behavior includes hardware ECC layout chosen by generic NAND core and channel-specific 16-bit bus configuration.

Dependencies and integration points: it uses raw NAND legacy callbacks, MTD registration, `linux/platform_data/txx9/ndfmc.h`, platform channel masks/timing flags, and optional PM resume. There is no DT parsing in this file.

Risks: probe does not fail if an enabled channel allocation, scan, or registration fails; it continues and can return success with fewer MTDs than requested. Platform data is assumed valid before dereferencing. Timing fields are clamped to 4-bit values, so bad GBus clock data can silently produce marginal timings. HWECC reads ECC bytes in a controller-specific byte order and corrects in 256-byte chunks. Dummy-write latch behavior is platform-flag dependent.

Test signals: controller reset completion, printed HOLD/SPW values matching board timing, every channel in `ch_mask` appearing as an MTD, CS selection when multiple channels are active, 16-bit channel READID/data transfer, HWECC correction over 256- and 512-byte page chunks, dummy-write platforms, and resume restoring NDFSPR/NDFMCR state.
