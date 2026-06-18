# sources/distributed-fs/ceph-client/drivers/scsi/jazz_esp.c

Purpose: platform front-end for NCR ESP SCSI on MIPS JAZZ systems, wiring the generic `esp_scsi` core to JAZZ memory-mapped registers, VDMA, IRQ, and platform-device resources.

Important APIs and functions: `jazz_esp_ops` provides register read/write, interrupt-pending, DMA reset/drain/invalidate, DMA command submission, and DMA error callbacks to the ESP core. `esp_jazz_probe()` allocates `Scsi_Host`, initializes `struct esp`, obtains register and DMA resources, allocates a coherent command block, requests IRQ, sets SCSI ID and clock, and registers the ESP host. `esp_jazz_remove()` unregisters and frees those resources.

Control flow: DMA command submission programs transfer count registers, disables VDMA, selects VDMA direction using ESP write semantics, programs address/count, enables VDMA, then sends the ESP command. Probe unwinds in reverse order on resource failures. Remove unregisters from SCSI first, then frees IRQ, command block, and host.

State and persistence: state lives in the allocated SCSI host/private ESP object, hardware registers, VDMA controller, and coherent command block. No persistent state exists.

Dependencies and integration: depends on MIPS JAZZ platform headers, `jazzdma` VDMA helpers, platform-device resources, shared IRQ handling through `scsi_esp_intr`, and the generic ESP SCSI core.

Risks and test signals: direction mapping between ESP write and DMA mode is hardware-specific and easy to regress. Tests/signals include successful platform probe, IRQ delivery, DMA error reporting for `R4030_MEM_INTR`/`R4030_ADDR_INTR`, command completion under read/write workloads, and correct cleanup after probe failures.
