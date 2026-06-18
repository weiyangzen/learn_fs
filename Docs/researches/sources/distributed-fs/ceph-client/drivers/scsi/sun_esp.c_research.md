<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun_esp.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sun_esp.c

## Purpose
`sun_esp.c` is the SPARC SBUS/Open Firmware front-end for the generic ESP SCSI core. It supports classic ESP/FAS and HME-style FAS366 arrangements, maps DMA and ESP registers from OF platform devices, derives initiator/clock/burst/differential properties, and supplies SBUS-specific DMA operations to `esp_scsi.c`.

## Important APIs, Types, And Functions
`enum dvma_rev` classifies DMA revisions. The `sbus_esp_ops` table implements ESP register access, IRQ pending checks, DMA reset/drain/invalidate/send/error callbacks. Setup helpers include `esp_sbus_setup_dma()`, `esp_sbus_map_regs()`, `esp_sbus_map_command_block()`, `esp_sbus_register_irq()`, `esp_get_scsi_id()`, `esp_get_differential()`, `esp_get_clock_params()`, `esp_get_bursts()`, and `esp_sbus_get_props()`. Platform lifecycle is `esp_sbus_probe()`, `esp_sbus_probe_one()`, and `esp_sbus_remove()`.

## Control Flow
OF matching binds names `SUNW,esp`, `SUNW,fas`, and `esp`. Probe finds the DMA platform device from the parent `espdma`/`dma` node or treats `SUNW,fas` as HME with combined resources. `esp_sbus_probe_one()` allocates a SCSI host, sets max target ID by HME capability, records wide capability for HME, maps DMA and ESP registers, allocates the command block, requests IRQ, reads OF properties, clears ESC1 reset state if necessary, stores driver data, and registers with the ESP core.

DMA reset first normalizes the DMA engine based on revision. HME reset programs parity/timing/interrupt/burst/SBUS64 bits in `prev_hme_dmacsr`, waits for pending reads to clear, and resets address/count state. Other revisions set 2-clock/3-clock, burst, add-enable, or FIFO behavior as needed. `sbus_esp_send_dma_cmd()` handles FASHME specially by programming 24-bit ESP transfer count, issuing the ESP command before DMA CSR/address/count enable, and preserving HME CSR state; other revisions enable DMA, optionally set ESC1 byte count, write DMA address, then issue the ESP command. Remove unregisters ESP, disables interrupts, frees IRQ/DMA memory, unmaps both register resources, drops the SCSI host, clears driver data, and releases the DMA device reference.

## State And Persistence Behavior
State is volatile `struct esp` state plus DMA revision, burst mask, HME previous CSR image, OF-derived SCSI ID/clock/differential flags, mapped register pointers, IRQ, and command-block DMA memory. There is no persistent state.

## Dependencies And Integration Points
The driver integrates OF platform discovery, SBUS IO helpers, SPARC DMA capability helpers (`sbus_can_dma_64bit()`, `sbus_can_burst64()`, `sbus_set_sbus64()`), Linux IRQ/DMA APIs, and the generic ESP SCSI core. It also interacts with FC/SCSI-style SCSI target behavior indirectly through `esp_scsi`.

## Risks
Risks are revision-specific DMA programming differences, HME CSR shadow corruption, OF property fallback mistakes, DMA node lifetime/reference handling, FIFO drain/invalidate timeouts, resource-index differences between HME and non-HME devices, and SBUS64/burst negotiation mismatches. The probe path must unwind mapped resources and command-block memory precisely.

## Test Signals
Test OF matches for `SUNW,esp`, `SUNW,fas`, and `esp`; parent-DMA versus HME resource topology; DMA revisions `DMA_VERS0`, `DMA_ESCV1`, `DMA_VERS1`, `DMA_VERS2`, `DMA_VERHME`, and `DMA_VERSPLUS`; burst property intersections; SCSI ID property fallback; differential flag handling; HME and non-HME DMA send paths; drain/invalidate timeouts; remove cleanup; and `scsi_esp_register()`/IRQ/command-block failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun_esp.c -->
