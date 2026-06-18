# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/omap2.c

Purpose: this is the TI OMAP2+ GPMC NAND glue driver. It connects raw NAND to the GPMC FIFO/register interface, supports polled/prefetch/DMA/IRQ transfer modes, implements Hamming and BCH ECC modes, integrates with the ELM BCH decoder, and registers an MTD device from Device Tree.

Important APIs, types, and functions: `struct omap_nand_info` stores the embedded `nand_chip`, GPMC chip select, transfer mode, ECC mode, ELM node/device, DMA channel, IRQs, FIFO/register pointers, ready GPIO, and ECC page grouping. Controller ops are `omap_nand_attach_chip()`, `omap_nand_detach_chip()`, and `omap_nand_exec_op()`. Major helpers cover prefetch setup/reset, DMA transfer, IRQ transfer, Hamming ECC, BCH ECC generation, ELM correction, BCH page read/write, and OOB layout.

Control flow: probe parses `reg`, `ti,elm-id`/`elm_id`, `ti,nand-ecc-opt`, and optional `ti,nand-xfer-type`, obtains GPMC NAND ops/registers, maps the FIFO resource, initializes a shared GPMC `nand_controller`, reads optional ready GPIO, assigns default data I/O callbacks, runs `nand_scan()`, and registers MTD. Attach selects data-transfer callbacks, requests DMA or IRQs when configured, validates ECC dependencies, then wires ECC geometry/callbacks and OOB layouts for software Hamming, hardware Hamming, BCH with software correction, or BCH with ELM correction.

State and persistence: state includes selected transfer and ECC modes, DMA channel, interrupt completions, ELM device reference, GPMC register programming, and ECC grouping fields (`neccpg`, `nsteps_per_eccpg`, `eccpg_size`, `eccpg_bytes`). Runtime flash persistence is normal NAND media; the driver itself maintains no on-disk state. Remove releases BCH resources, DMA, MTD registration, and NAND cleanup.

Dependencies and integration points: the file depends on GPMC NAND platform ops, raw NAND controller APIs, DMAengine, GPIO ready polling, ELM platform data, software BCH library, OMAP BCH Kconfig support, MTD OOB layout helpers, and OF match data from OMAP NAND platform headers.

Risks: many ECC modes have different OOB reservations and boot-ROM compatibility bytes; wrong DT choices can make existing media unreadable. Prefetch/DMA/IRQ paths have fallback behavior but depend on GPMC FIFO status and completion ordering. ELM availability is required for hardware BCH correction. Erased-page bitflip handling is custom and must stay aligned with NAND core behavior. The shared controller serializes access to the GPMC ECC engine across instances.

Test signals: cover all transfer modes, ready GPIO and soft wait paths, Hamming and BCH4/8/16 ECC modes, ELM missing/present cases, OOB layout size checks, erased-page bitflip correction, BCH page and subpage writes, DMA fallback for invalid buffers, IRQ FIFO/count completions, DT parsing failures, MTD registration, and cleanup after attach/probe errors.
