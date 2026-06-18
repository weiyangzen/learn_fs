# sources/distributed-fs/ceph-client/drivers/scsi/scsi_debugfs.h

Purpose: declares the SCSI debugfs request formatting hook shared between the SCSI queueing code and the small implementation in `scsi_debugfs.c`.

Important APIs/types/functions: forward declares `struct request` and `struct seq_file`, then exposes `void scsi_show_rq(struct seq_file *m, struct request *rq);`.

Control flow: there is no executable logic. Inclusion allows `scsi_lib.c` to assign `.show_rq = scsi_show_rq` in blk-mq operations when block debugfs support is enabled.

State and persistence: no state is stored or persisted.

Dependencies and integration: intentionally avoids pulling full block or seq headers into includers by using forward declarations. It integrates `scsi_debugfs.c` with blk-mq debugfs setup in `scsi_lib.c`.

Risks: the declaration must stay synchronized with the implementation and the block-layer callback signature. Any signature drift will be caught at compile time.

Test signals: build with `CONFIG_BLK_DEBUG_FS` enabled and disabled to ensure the declaration remains sufficient for both configurations.
