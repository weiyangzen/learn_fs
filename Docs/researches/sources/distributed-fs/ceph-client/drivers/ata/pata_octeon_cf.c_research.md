# sources/distributed-fs/ceph-client/drivers/ata/pata_octeon_cf.c

## Purpose
Provides the Cavium OCTEON bootbus CompactFlash libata driver. It supports 8-bit PIO, 16-bit PIO, and 16-bit True IDE with optional bootbus DMA, all described by Open Firmware properties.

## Important APIs, Types, And Functions
`struct octeon_cf_port` keeps the hrtimer, ATA port pointer, DMA state, chip selects, True IDE flag, and DMA register base. Timing helpers include `ns_to_tim_reg()`, `octeon_cf_set_boot_reg_cfg()`, `octeon_cf_set_piomode()`, and `octeon_cf_set_dmamode()`. Data/taskfile hooks include `octeon_cf_data_xfer8()`, `octeon_cf_data_xfer16()`, `octeon_cf_tf_read16()`, `octeon_cf_tf_load16()`, `octeon_cf_softreset16()`, and `octeon_cf_exec_command16()`. DMA control is split across `octeon_cf_dma_setup()`, `octeon_cf_dma_start()`, `octeon_cf_interrupt()`, `octeon_cf_delayed_finish()`, and `octeon_cf_dma_finished()`.

## Control Flow
Probe reads `cavium,true-ide`, `cavium,bus-width`, bootbus chip-select registers, and an optional DMA-engine phandle, maps the command/control regions, selects the appropriate SFF overrides, and activates a one-port host. PIO commands fall through `ata_sff_qc_issue()`. DMA commands load the taskfile, submit one scatterlist segment to the bootbus DMA engine, advance to the next segment on DMA-done interrupts, then either finish immediately or poll with an hrtimer until the CF card clears BUSY/DRQ.

## State And Persistence
Driver state is device-managed except for hardware state in OCTEON bootbus CS timing registers and DMA CSRs. `ap->private_data` and `pdev->dev.platform_data` point at `struct octeon_cf_port`; `dma_finished` and `qc->cursg` track active DMA progress under `host->lock`.

## Dependencies And Integration Points
Integrates libata SFF/BMDMA-like hooks, OF address/property parsing, OCTEON `cvmx_*` CSR accessors, DMA mask setup, hrtimers, IRQ delivery from the companion DMA platform device, and libata tracepoints.

## Risks And Edge Cases
`octeon_cf_ops` is a static operations object that probe mutates based on board mode, so multiple differently wired devices would share changed callbacks. DMA is opt-in by module parameter and only valid in True IDE mode. DMA size is limited to the 20-bit bootbus counter, and shutdown must quiesce DMA and pulse reset. Busy-after-DMA timing is card dependent, making the interrupt/hrtimer handoff critical.

## Test Signals
Boot DT variants for 8-bit, 16-bit non-True-IDE, and True IDE DMA; PIO0-6 timing programming; odd-byte 16-bit transfers; LBA48 HOB taskfile reads; multi-segment DMA; DMA timeout/error injection; unload or shutdown during no-DMA and DMA cases.
