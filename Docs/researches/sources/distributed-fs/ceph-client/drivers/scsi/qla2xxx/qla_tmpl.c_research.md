# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_tmpl.c

Purpose: executes 27xx firmware-dump templates to capture adapter registers, RAM, queues, trace buffers, shadow pointers, and firmware/driver metadata into qla2xxx dump buffers.

Important APIs/functions: public entry points are `qla27xx_fwdt_calculate_dump_size()`, `qla27xx_fwdt_template_size()`, `qla27xx_fwdt_template_valid()`, `qla27xx_mpi_fwdump()`, and `qla27xx_fwdump()`. The private dispatcher maps entry types 0, 255, and 256-278 to handlers for reads, writes, RAM dumps, queues, FCE/EFT buffers, scratch records, remote registers/RAM, PCI config, conditional entries, and PEP register access.

Control flow: validation checks template type and checksum. Size calculation walks entries with `buf == NULL`, increasing `len` without touching hardware side effects. Capture copies the template into the output buffer, edits timestamp/driver/firmware fields, then walks entries with a live buffer. Entries may modify the copied template, skip unsupported regions by setting `DRIVER_FLAG_SKIP_ENTRY`, or abort by returning `INVALID_ENTRY`.

State and persistence: dumps update `fw_dump_len`, `fw_dumped`, `mpi_fw_dump_len`, `mpi_fw_dumped`, and `num_mpi_reset`, then post a firmware-dump uevent. Captured data persists only in allocated in-kernel dump buffers until userspace consumes or clears it.

Dependencies and integration: uses qla2xxx register accessors, mailbox RAM dump helpers, queue maps, target-mode ATIO rings, PCI config reads, `jiffies`, hardware locks, and uevents. Target-mode queue capture is gated by `QLA_TGT_MODE_ENABLED()`.

Risks: template size/checksum trust boundaries, insufficient output sizing, buffer pointer arithmetic, hardware side effects from write/pause/reset entries, lock misuse, and stale template entries for missing queues or buffers. Test signals include valid/invalid checksum templates, no-buffer paths, repeated MPI dumps using spare space, missing FCE/EFT buffers, RAM dump mailbox failures, and residual-size logging.
