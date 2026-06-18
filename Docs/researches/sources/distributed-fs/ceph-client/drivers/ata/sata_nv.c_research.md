# sources/distributed-fs/ceph-client/drivers/ata/sata_nv.c

## Purpose
Implements the libata low-level driver for NVIDIA nForce SATA controllers. It supports legacy BMDMA-style controllers, NF2/NF3 and CK804 interrupt layouts, CK804/MCP04 ADMA with NCQ, MCP5x software NCQ, optional MSI, reset quirks, hotplug handling, and device-specific NCQ limitations.

## Important APIs, Types, And Functions
- Module parameters `adma`, `swncq`, and `msi` choose optional ADMA, software NCQ, and MSI behavior.
- `enum nv_host_type`, `nv_pci_tbl`, `nv_port_info`, and `struct nv_pi_priv` map PCI IDs to port ops, interrupt handlers, and SCSI host templates.
- ADMA state uses `struct nv_adma_port_priv`, `struct nv_adma_cpb`, and `struct nv_adma_prd`; major functions are `nv_adma_port_start`, `nv_adma_qc_prep`, `nv_adma_qc_issue`, `nv_adma_interrupt`, `nv_adma_error_handler`, `nv_adma_sdev_configure`, `nv_adma_register_mode`, and `nv_adma_mode`.
- Software NCQ state uses `struct nv_swncq_port_priv` and `struct defer_queue`; major functions are `nv_swncq_qc_prep`, `nv_swncq_qc_issue`, `nv_swncq_host_interrupt`, `nv_swncq_sdbfis`, `nv_swncq_dmafis`, and `nv_swncq_error_handler`.
- Generic paths include `nv_host_intr`, `nv_generic_interrupt`, `nv_nf2_interrupt`, `nv_ck804_interrupt`, `nv_scr_read`, `nv_scr_write`, `nv_hardreset`, freeze/thaw variants, `nv_init_one`, `nv_pci_device_resume`, and host stop helpers.

## Control Flow
Probe first rejects non-SATA NVIDIA IDE-function matches by requiring all six PCI BARs. It enables the PCI device, optionally upgrades CK804 to ADMA or MCP5x to SWNCQ according to module parameters, prepares a libata BMDMA host, maps BAR5, configures SCR addresses, enables SATA register space on CK804-or-newer chips, initializes ADMA or SWNCQ mode if selected, optionally enables MSI, and activates the host through the selected interrupt handler.

Legacy interrupts either scan active tags directly or decode NVIDIA per-port interrupt status bits before calling `nv_host_intr`, which freezes on hotplug, completes BMDMA commands on device IRQs, and clears status for idle interrupts. Reset flow intentionally prefers softreset during boot and error handling and uses `nv_hardreset` only for post-boot probing of empty ports; signature acquisition is deliberately reported as unreliable by returning `-EAGAIN`.

ADMA mode allocates coherent CPB/APRD memory after first allocating 32-bit legacy BMDMA resources, programs CPB bases, and starts ports in register mode. Per-device configuration disables ADMA and lowers DMA limits when ATAPI is present because ATAPI must use the legacy 32-bit DMA path. ADMA command prep builds a CPB taskfile and in-CPB or external APRD list, marks the CPB valid only after barriers, and issue appends the tag to hardware. The ADMA interrupt path handles register-mode fallback, notifier/error bitmaps, hotplug/timeouts/SError freezes, CPB response inspection, multi-tag completion, and notifier clear ordering required by NVIDIA.

SWNCQ mode uses normal taskfile issue for one NCQ command at a time while queueing additional tags in `defer_queue`. DMA setup FIS interrupts program per-tag PRD tables and start BMDMA, SDB FIS interrupts compare software active bits with `SCR_ACTIVE`, complete done tags, and reissue or dequeue commands when device-to-host FIS sequencing requires it. Hotplug and illegal FIS sequences freeze the port for libata EH.

## State And Persistence
`nv_host_priv` persists the selected host type. ADMA port state keeps coherent CPB/APRD pointers, BAR5 control/generic/notifier clear addresses, the effective ADMA DMA mask, mode flags for register fallback and ATAPI setup, and the last NCQ mode issued. SWNCQ port state keeps coherent PRD tables, MMIO pointers for SActive/IRQ/tag registers, a software active bitmap, deferred tag FIFO, last issued tag, and bitmaps of observed D2H/DMA/SDB FIS activity. PCI config register `NV_MCP_SATA_CFG_20` persists SATA-space, port enable, and ADMA port bits and is restored on resume. Freeze/thaw paths persist interrupt masks in chipset-specific MMIO or SCR register blocks.

## Dependencies And Integration Points
The driver depends on PCI managed resource helpers, libata BMDMA/SFF/EH/NCQ APIs, SCSI queue-limit callbacks, tracepoints for taskfile and BMDMA status, DMA mask management, PCI MSI, and NVIDIA PCI device IDs/config registers. ADMA and SWNCQ integrate with libata queue depth through `ata_ncq_sdev_groups` and `ata_scsi_change_queue_depth`, while fallback paths reuse `ata_bmdma_port_start`, `ata_bmdma_qc_issue`, `ata_bmdma_error_handler`, and standard SCR helpers.

## Risks And Edge Cases
Hardreset behavior is intentionally conservative because several NVIDIA generations fail link bring-up or device signature capture after hardreset. ADMA cannot safely handle ATAPI and must coordinate per-device queue limits with a shared PCI DMA mask. Entering register mode while ADMA commands are outstanding aborts command processing, so result taskfiles for NCQ are rejected. NVIDIA notifier clearing requires both ports' clear registers to be written together. SWNCQ sequencing is fragile: missing D2H FIS, backout interrupts, stale `SCR_ACTIVE`, and deferred tag FIFO errors can mis-complete or reissue commands incorrectly. Known Maxtor devices on MCP51/MCP55 early revisions have SWNCQ disabled by reducing queue depth to one.

## Test Signals
Important tests include BAR-count rejection of IDE functions, generic/NF2/CK804 interrupt masking and hotplug handling, boot probing via softreset with post-boot hardreset on empty ports, ADMA DMA/NCQ completion and CPB error classification, ATAPI fallback that changes DMA mask and segment limits, notifier clear behavior across both ports, ADMA suspend/resume with ATAPI port bits restored, SWNCQ deferred multi-tag issue/completion, backout and missing-D2H reissue paths, Maxtor queue-depth disablement, and MSI activation when requested.
