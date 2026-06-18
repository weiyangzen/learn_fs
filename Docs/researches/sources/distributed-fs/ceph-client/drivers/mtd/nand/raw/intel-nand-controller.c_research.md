# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/intel-nand-controller.c

Purpose: this is the Intel LGM External Bus Unit NAND controller driver. It combines a low-speed EBU command/address/data path with a high-speed NAND engine and DMA channels for hardware-ECC page reads/writes.

Important APIs, types, and functions: `struct ebu_nand_controller` owns the embedded `nand_controller`, single `nand_chip`, EBU/HSNAND register mappings, TX/RX DMA channels, completion, clock, chip-select data, and `nd_para0` ECC/page geometry register value. Key functions include `ebu_nand_set_timings()`, `ebu_nand_exec_op()`, `ebu_dma_start()`, `ebu_nand_trigger()`, `ebu_nand_read_page_hwecc()`, `ebu_nand_write_page_hwecc()`, `ebu_nand_attach_chip()`, and probe/remove.

Control flow: probe maps named resources `ebunand`, `hsnand`, `nand_csN`, and `addr_selN`, reads the child node's chip select, enables the clock, requests TX/RX DMA channels, programs address selection, attaches the child node to the NAND chip, initializes controller ops, scans one target, and registers MTD. Generic operations are handled by `exec_op()`, which selects the chip in `EBU_CON` and writes command/address/data bytes through memory offsets. Hardware-ECC page operations call `ebu_nand_trigger()`, perform DMA over the full page data area, optionally read/write the first 8 OOB bytes through message registers, clear the GO bit, and return.

State and persistence: persistent state includes active chip select, EBU address-selection register value, DMA channels, `nd_para0` computed during attach, and EBU bus timings. Runtime operation state lives in HSNAND CTL/CTL1/CTL2/PARA/CMSG/interrupt registers and DMA completion state.

Dependencies and integration points: the driver depends on raw NAND `exec_op`, `setup_interface`, hardware ECC callbacks, DMAengine, platform named resources, clocks, OF compatible `intel,lgm-ebunand`, and MTD OOB layout APIs. It requires an MTD label from the child node.

Risks: `ebu_dma_start()` maps buffers with the DMA channel device but unmaps with `ebu_host->dev`, which may be a different device. The successful DMA path returns without unmapping the buffer, which is a DMA mapping leak. `WAITRDY` multiplies timeout milliseconds by 1000 and passes that to a helper named in milliseconds but implemented as a microsecond poll timeout. Hardware ECC has limited page/block geometry encodings and rejects unsupported OOB capacity. The write-complete poll waits for `!(val & WR_C)`, which is easy to misread against the interrupt-status semantics.

Test signals: exercise ONFI identification via `exec_op`, SDR timing setup writes, supported 512/1024-byte ECC sizes and strengths, DMA read/write completion and timeout cleanup, OOB message register handling, MTD label validation, resource-name validation, and removal cleanup including DMA channel release and EBU disable.
