# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-loader-skl.c

Purpose: `hda-loader-skl.c` implements the Skylake-specific code-loader DMA path. Unlike newer HDA code that reuses HDAC stream abstractions, this file manually programs the CLDMA stream, BDL, SPB FIFO, interrupts, and ROM status polling for firmware download.

Important APIs: the exported entry point is `hda_dsp_cl_boot_firmware_skl()`. Internal helpers allocate DMA buffers, build a single-fragment BDL, clear/setup/run the CLDMA stream, configure SPB FIFO, enable/disable CLDMA interrupts, initialize the DSP core and ROM, copy firmware chunks into the DMA buffer, wait for CLDMA completion via `hda->waitq`, and clean up.

Control flow: boot initializes the DSP with `cl_dsp_init_skl()`, retries once on failure, waits for ROM INIT_DONE, strips the firmware to payload offset, copies it in chunks no larger than 32 pages, triggers CLDMA for each chunk, waits for interrupts except the last transfer, then polls for `FSR_STATE_ROM_BASEFW_ENTERED`. On success it stops and clears CLDMA, frees buffers, and returns the init core mask. On failure it dumps PCI/mailbox state, powers down the init core, stops CLDMA, cleans up, and returns the error.

State and persistence behavior: runtime state includes two temporary DMA buffers, CLDMA stream registers, SPB FIFO registers, ADSPIC CL_DMA interrupt bit, `hda->code_loading`, and the shared wait queue. Firmware payload offset is taken from `sdev->basefw`.

Dependencies and integration: this file depends on HDA DSP core helpers, SOF firmware metadata, low-level register access, and `hda_dsp_check_ipc_irq()` clearing `hda->code_loading` for CLDMA interrupts.

Risks and test signals: the single-fragment physical-memory assumption is deliberate but fragile. Risks include timeout waiting for code-loading interrupts, wrong BDL alignment, stale CLDMA interrupt status, and improper cleanup after partial load. Test signals include SKL firmware boot, oversized-but-valid firmware chunking, CLDMA timeout diagnostics, ROM status progression, and no DMA buffer leaks after retry/failure.
