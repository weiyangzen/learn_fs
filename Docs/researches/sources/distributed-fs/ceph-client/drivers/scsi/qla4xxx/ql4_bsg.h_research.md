# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_bsg.h

Purpose: shared vendor command numbers for qla4xxx iSCSI BSG handling.

Important APIs/types: defines command IDs `QLISCSI_VND_READ_FLASH` through `QLISCSI_VND_DIAG_TEST`, plus diagnostic subcommands for DDR, on-chip memory, NVRAM, flash ROM, internal/external loopback, DMA transfer, and self-tests.

Control flow: `ql4_bsg.c` switches on these constants in the first vendor command word and diagnostic subcommand words to choose management operations.

State and persistence: no state; constants identify operations that may read or modify persistent flash/NVRAM and runtime adapter configuration.

Dependencies and integration: must match userspace management tools and qla4xxx firmware mailbox expectations.

Risks: ABI number changes would break userspace; comments note some diagnostics are ISP4XXX-only, so dispatch must keep adapter-family checks. Test signals are userspace BSG command compatibility and invalid subcommand rejection.
