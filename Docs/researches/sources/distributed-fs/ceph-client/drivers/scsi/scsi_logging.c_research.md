# sources/distributed-fs/ceph-client/drivers/scsi/scsi_logging.c

Purpose: centralizes SCSI command, device, result, and sense logging. It produces consistent `dev_printk()` prefixes containing disk name and request tag, formats CDB opcode/service-action names, and decodes normalized sense key/ASC/ASCQ data for diagnostics.

Important APIs/types/functions: exported print helpers are `sdev_prefix_printk()`, `scmd_printk()`, `__scsi_format_command()`, `scsi_print_command()`, `scsi_print_sense_hdr()`, `__scsi_print_sense()`, `scsi_print_sense()`, and `scsi_print_result()`. Internal helpers reserve small GFP_ATOMIC buffers, build headers with `sdev_format_header()`, map opcodes through `scsi_opcode_sa_name()`, and format or dump sense data through `scsi_format_sense_hdr()`, `scsi_format_extd_sense()`, and `scsi_log_dump_sense()`.

Control flow: callers request a log buffer, prefix it with optional disk name and tag, append formatted command/result/sense text, emit via `dev_printk()`, and free the buffer. Long CDBs are split into multiple hex-dump lines. Sense logging first tries `scsi_normalize_sense()`; normalized sense prints decoded key and additional sense text, otherwise raw sense bytes are hex dumped.

State and persistence: no persistent state is maintained. Logging reads command, request, device, sense, jiffies, and opcode tables, allocates transient buffers, and writes kernel log messages.

Dependencies and integration: used by SCSI error handling, queueing, ioctl handling, ULDs, and debugfs. It depends on SCSI opcode/sense lookup helpers, request tag/disk metadata, kernel printk/device logging, and `SCSI_SENSE_BUFFERSIZE`.

Risks: runs in atomic and error paths, so allocation uses `GFP_ATOMIC` and silently drops logs on allocation failure. The fixed 128-byte buffer can truncate verbose output; WARN checks catch overflow assumptions. Logging must avoid dereferencing missing `rq->q`/disk metadata, handled by `scmd_name()`.

Test signals: enable SCSI logging levels, issue normal CDBs, vendor/reserved opcodes, variable-length CDBs, long CDBs, normalized and malformed sense buffers, recovered errors, and failed commands with old request tags to verify readable non-overflowing log output.
