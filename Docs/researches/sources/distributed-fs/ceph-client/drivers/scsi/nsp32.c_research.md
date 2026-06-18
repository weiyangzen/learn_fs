# sources/distributed-fs/ceph-client/drivers/scsi/nsp32.c

Purpose: PCI/CardBus SCSI host adapter driver for Workbit NinjaSCSI-32Bi/UDE hardware. It registers a PCI driver and SCSI host, initializes ASIC registers, builds coherent DMA SG/autoparam tables, negotiates SDTR synchronous transfer parameters, drives AutoSCSI selection/phase handling, and manages reset/suspend/resume.

Important APIs/functions: `nsp32_probe()`, `nsp32_detect()`, `nsp32_remove()`, `nsp32_release()` own lifecycle. `nsp32_queuecommand()` is the SCSI entry point; it delegates to SG setup, IDENTIFY/SDTR construction, and `nsp32_selection_autopara()` or `nsp32_selection_autoscsi()`. `do_nsp32_isr()` handles AutoSCSI, FIFO, phase-change, reset, timer, and PCI/BMCNT interrupts. Message and negotiation flow is in `nsp32_msgin_occur()`, `nsp32_msgout_occur()`, `nsp32_busfree_occur()`, `nsp32_analyze_sdtr()`, and sync-table helpers.

Control flow/state: the driver is single-command-at-a-time through `data->CurrentSC`. Attach allocates `nsp32_hw_data`, coherent SG and autoparam memory, initializes per-target and per-LUN state, reads EEPROM sync limits, resets the bus, requests IRQ/I/O regions, and scans. Runtime state includes current nexus pointers, per-target SDTR flags/registers, per-LUN SG progress, message buffers, EEPROM-derived limits, and DMA addresses. EEPROM is read only at probe; settings are not persisted back.

Dependencies/integration: Linux PCI, SCSI midlayer, DMA mapping, I/O/MMIO primitives, `nsp32.h`, `nsp32_io.h`, and optional `nsp32_debug.c`. It integrates through `struct pci_driver` and `struct scsi_host_template`.

Risks/test signals: risks include legacy busy waits, complex message/reselection logic, SG segment limit of 64 KiB, mostly unsupported MMIO/PIO transfer modes, and TODOs for illegal phase/BMCNT/SCSI-3 behavior. Test via module probe, SCSI scan, read/write completion, SDTR status in host info, abort/host reset, EEPROM-missing fallback, selection timeout, bus reset, suspend/resume, and card removal handling.
