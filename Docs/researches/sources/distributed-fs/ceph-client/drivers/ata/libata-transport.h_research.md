# sources/distributed-fs/ceph-client/drivers/ata/libata-transport.h

## Purpose
`libata-transport.h` is the small internal header that shares ATA transport-class declarations between libata source files. It avoids exposing transport setup details through the public libata API while letting SCSI and core code reference the transport template and link lifecycle helpers.

## Important APIs, Types, And Functions
The header declares `extern struct scsi_transport_template ata_scsi_transportt`, `int ata_tlink_add(struct ata_link *link)`, `void ata_tlink_delete(struct ata_link *link)`, `__init int libata_transport_init(void)`, and `void __exit libata_transport_exit(void)`. It depends on prior declarations of `struct ata_link` and SCSI transport types from included libata/SCSI headers.

## Control Flow
There is no executable control flow. The declarations support module initialization/exit, SCSI host setup, and port/link device-model lifecycle implemented in `libata-transport.c`.

## State And Persistence
The header owns no state. It declares access to the global `ata_scsi_transportt` template and transport init/exit routines that manage driver-model state elsewhere.

## Dependencies And Integration Points
It is included by `libata-scsi.c` to assign `shost->transportt` and by `libata-transport.c` for self-consistency. The include guard `_LIBATA_TRANSPORT_H` prevents duplicate declarations.

## Risks And Edge Cases
The header is intentionally narrow. Signature drift between this header and `libata-transport.c` would break builds. Because it is internal, adding broad declarations here can increase coupling between libata subsystems.

## Test Signals
Build coverage with `CONFIG_ATA` and SCSI transport enabled is the primary signal. Link-time failures would catch missing `ata_scsi_transportt`, `ata_tlink_add/delete`, or transport init/exit definitions.
