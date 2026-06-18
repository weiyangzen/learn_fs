# sources/distributed-fs/ceph-client/drivers/scsi/scsi_debugfs.c

Purpose: provides the SCSI-specific blk-mq debugfs request printer used when `CONFIG_BLK_DEBUG_FS` wires `scsi_show_rq()` into the SCSI `blk_mq_ops`. It formats SCSI command metadata that the generic block layer cannot know: CDB text, retry counters, result code, timeout age, command flags, and whether the command is currently linked on host error-handling lists.

Important APIs/types/functions: `scsi_show_rq(struct seq_file *m, struct request *rq)` is the only externally declared function. It obtains the command with `blk_mq_rq_to_pdu()`, formats initialized CDBs through `__scsi_format_command()`, and prints `cmd->retries`, `cmd->allowed`, `cmd->result`, request timeout, allocation age, and `SCMD_*` flag names. `scsi_flags_show()` maps set bits to `TAGGED`, `INITIALIZED`, and `LAST` where known. `scsi_cmd_list_info()` scans `shost->eh_abort_list` and `shost->eh_cmd_q` under `host_lock` to annotate commands already owned by error handling.

Control flow: debugfs calls into `scsi_show_rq()` for a live request. The function only emits command details if `SCMD_INITIALIZED` is set, then always emits the flag set. Error-handler list detection is a read-only locked walk and returns a constant string, so no list state changes occur.

State and persistence: this file has no durable state. It reads volatile request, command, jiffies, and host error-handler list state and writes only to the supplied `seq_file`.

Dependencies and integration: depends on block request private data layout from `scsi_lib.c`, CDB formatting from `scsi_logging.c`, SCSI host locking, and blk debugfs registration in `scsi_mq_ops`.

Risks: output is diagnostic but runs against live commands, so lock coverage for error-handler lists matters. Unknown command flag bits are printed numerically, which is robust but can make newly added flags less readable until the table is updated.

Test signals: enable block debugfs, issue normal and timed-out SCSI I/O, and inspect request debugfs output for initialized commands, passthrough commands, commands on `eh_abort_list`/`eh_cmd_q`, and unknown flag-bit formatting.
