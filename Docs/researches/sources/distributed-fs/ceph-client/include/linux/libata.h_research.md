# sources/distributed-fs/ceph-client/include/linux/libata.h

Purpose: exposes libata's core host, port, link, device, queued-command, error-handling, SATA, SFF, BMDMA, ACPI, PMP, SCSI translation, timing, and driver-template interfaces.

Important APIs and types: constants and flags describe quirks, taskfile fields, device/link/port/qc/host flags, timeouts, bus/HSM states, transfer masks, completion errors, LPM policies, EH actions, ACPI filters, and DMA masks. Core structs include `ata_taskfile`, `ata_host`, `ata_port`, `ata_link`, `ata_device`, `ata_queued_cmd`, `ata_eh_info`, `ata_eh_context`, `ata_port_operations`, `ata_reset_operations`, `ata_port_info`, and `ata_timing`. Helper APIs allocate/register/activate/detach hosts, queue SCSI commands, classify devices, manage xfer modes, complete QCs, run EH, debounce SATA links, read/write SCRs, initialize SFF/BMDMA/PCI hosts, and define SCSI host templates.

Control flow: a low-level ATA driver supplies `ata_port_operations` and port info, allocates or activates an `ata_host`, libata probes links/devices, translates SCSI commands into ATA queued commands, issues them through driver callbacks, handles interrupts/completion, and schedules EH for timeouts, resets, hotplug, or media/device errors. SATA/PMP/SFF/BMDMA sections provide optional protocol-specific flows.

State and persistence: state is in-memory per host/port/link/device/qc, including identify data, log pages, queue masks, EH rings, LPM policy, transfer modes, and SCSI device associations. Persistent media state is accessed through ATA commands; this header owns no on-disk format.

Dependencies and integration points: depends on ATA protocol definitions, SCSI host/device APIs, DMA/scatterlists, PCI/platform/ACPI/PM, timers/workqueues, and optional SATA/PMP/SFF/BMDMA configs. It is the primary contract between controller drivers and the libata/SCSI stack.

Risks and test signals: risks include flag-bit drift, callback inheritance misuse, queue tag races, EH state-machine regressions, reset timeout handling, NCQ/PMP exclusion bugs, ACPI filter mistakes, SCSI template module ownership, and config fallback mismatches. Test probe/remove, ATA/ATAPI/ZAC devices, NCQ priority, TRIM/FUA quirks, link power management, hotplug, suspend/resume, EH reset/retry, SFF/BMDMA interrupts, PCI/platform paths, and compile matrices.
