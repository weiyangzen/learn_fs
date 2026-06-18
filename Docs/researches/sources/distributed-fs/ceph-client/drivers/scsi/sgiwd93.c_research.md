# sources/distributed-fs/ceph-client/drivers/scsi/sgiwd93.c

## Purpose
Provides the SGI IP22 platform driver for WD33C93 SCSI controllers connected through the SGI HPC3 DMA engine. It adapts the shared `wd33c93` SCSI core to SGI hardware registers, interrupt delivery, and HPC descriptor-chain DMA.

## Important APIs, Types, And Functions
`struct ip22_hostdata` embeds `WD33C93_hostdata` and adds the DMA descriptor memory, DMA handle, and parent `device`. `struct hpc_chunk` wraps an `hpc_dma_desc` with padding to keep descriptors quadword-aligned. `sgiwd93_template` defines the SCSI host template using `wd33c93_queuecommand`, `wd33c93_abort`, and `wd33c93_host_reset`.

The important functions are `sgiwd93_probe`, `sgiwd93_remove`, `sgiwd93_intr`, `dma_setup`, `dma_stop`, `fill_hpc_entries`, `init_hpc_chain`, and exported `sgiwd93_reset`.

## Control Flow
The platform-driver init function registers a driver named `sgiwd93`. Probe obtains platform data containing WD register addresses, HPC register addresses, unit number, and IRQ. It allocates a `Scsi_Host` with `ip22_hostdata`, allocates one noncoherent page for HPC DMA descriptors, initializes the circular descriptor chain, points WD33C93 register access at SASR/SCMD offsets, configures sync/fast/burst DMA mode in the embedded WD hostdata, and calls `wd33c93_init` with `dma_setup` and `dma_stop` callbacks. It then requests the IRQ, registers the host with SCSI core, and scans the bus.

For interrupts, `sgiwd93_intr` takes the SCSI host lock and delegates to `wd33c93_intr`. For data movement, `dma_setup` records direction, rejects empty/bogus transfers as no-DMA, maps the current SCSI buffer with `dma_map_single`, fills the HPC descriptor list in chunks of at most 8192 bytes, appends an EOX descriptor, syncs descriptor memory for the device, writes the next-descriptor pointer, and starts HPC with direction-specific control bits. `dma_stop` stops or flushes HPC depending on direction, clears control, and unmaps the original DMA buffer.

Remove reverses probe: remove SCSI host, free IRQ, free noncoherent descriptor memory, and release the `Scsi_Host`.

## State And Persistence Behavior
All state is runtime-only and scoped to the platform device. The descriptor page is reused across commands; each DMA setup rewrites descriptors from the current `scsi_pointer`. The embedded `WD33C93_hostdata` persists controller settings and current DMA direction while the host exists. No state is stored on disk or across driver unload.

## Dependencies And Integration Points
This file depends on SGI MIPS platform headers (`hpc3`, `ip22`, `wd`), Linux platform-device and DMA APIs, SCSI host core, and the shared `wd33c93` driver. Hardware integration is through HPC3 SCSI registers and WD33C93 SASR/SCMD register windows supplied by platform data.

## Risks
The DMA path assumes the WD33C93 core uses `struct scsi_pointer` fields in the expected way. Descriptor limits and the 8192-byte chunking rule encode hardware behavior; changing them can create truncated or corrupt DMA. The file contains an explicit warning that abort/reset method signatures can be unsafe on 64-bit systems with memory outside compatible address spaces. Error handling in probe must preserve unwind order because IRQ registration, host registration, and descriptor allocation are independent resources.

## Test Signals
Signals are mainly platform/hardware tests: boot on SGI IP22 with the controller present, IRQ delivery under command load, DMA reads and writes over transfer sizes above and below 8192 bytes, abort and host-reset paths via SCSI error handling, remove/unbind cleanup, and DMA API debug checks for map/unmap balance. Build coverage requires the target architecture/platform headers that expose SGI HPC3 and WD platform data.
