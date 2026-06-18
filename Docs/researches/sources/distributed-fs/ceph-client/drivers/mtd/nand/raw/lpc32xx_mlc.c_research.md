# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/lpc32xx_mlc.c

Purpose: this is the NXP LPC32xx MLC NAND controller driver. It supports automatic hardware encode/decode for 512-byte subpages, controller/NAND-ready interrupts, optional PL080-style DMA, write-protect GPIO handling, fixed flash BBT placement, and DT-configured timing.

Important APIs, types, and functions: `struct lpc32xx_nand_cfg_mlc` stores DT timing fields. `struct lpc32xx_nand_host` stores the embedded `nand_chip`, platform data, clock, WP GPIO, MMIO base, IRQ, completions, DMA channel/config/buffers, and subpage count. Major functions are `lpc32xx_nand_setup()`, command/ready/wait helpers, `lpc32xx_xmit_dma()`, `lpc32xx_read_page()`, `lpc32xx_write_page_lowlevel()`, OOB read/write hooks, `lpc32xx_nand_attach_chip()`, probe/remove, and suspend/resume.

Control flow: probe maps registers, parses required `nxp,*` timing properties, gets optional WP GPIO, enables the clock, installs legacy command/ready/data addresses, resets and configures the MLC timing registers, optionally sets up DMA if global `use_dma` is enabled, requests the IRQ, scans one NAND target, and registers the MTD. Attach configures on-host ECC with 512-byte steps, strength 4, 10 ECC bytes, custom OOB layout, page/OOB callbacks, and subpage count. Reads issue a page read, start auto-decode for each subpage, wait for controller-ready, account ECC failures/corrections from `MLC_ISR`, and pull 512 data plus 16 OOB bytes from the controller buffer. Writes start auto-encode per subpage, push 512 data plus selected OOB bytes, wait ready, then finish program.

State and persistence: persistent state includes timing configuration, DMA buffers, completion objects, IRQ registration, WP GPIO state, clock state, and flash BBT absolute-page descriptors. Suspend enables write protect and disables the clock; resume reenables clock, reinitializes the controller, and disables write protect.

Dependencies and integration points: the driver uses legacy raw NAND callbacks, MTD partitions from platform/DT config, DMAengine fallback through `lpc32xx_mlc_platform_data`, IRQ completions, clock APIs, and compatible `nxp,lpc3220-mlc`.

Risks: DMA is controlled by a file-scope `use_dma` variable initialized to false and has no module parameter here. Some DMA waits ignore timeout return values. The driver assumes large-block, five-address-cycle MLC behavior and fixed 512-byte subpage ECC. `write_oob` is a no-op because automatic ECC conflicts with standalone OOB writes. Timing DT properties are mandatory and unchecked for division edge cases beyond nonzero.

Test signals: validate 2 KiB and 4 KiB page reads/writes, ECC failure/correction statistics, OOB layout per 16-byte subpage, IRQ completion for NAND/controller ready, suspend/resume WP and timing restore, probe failures for missing timings/WP/IRQ/DMA, and both FIFO and optional DMA transfer paths.
