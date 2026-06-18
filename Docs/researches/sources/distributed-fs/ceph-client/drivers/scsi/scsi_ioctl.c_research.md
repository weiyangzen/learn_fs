# sources/distributed-fs/ceph-client/drivers/scsi/scsi_ioctl.c

Purpose: implements common SCSI ioctl handling and userspace passthrough compatibility for block/SCSI devices. It supports SG_IO, deprecated `SCSI_IOCTL_SEND_COMMAND`, CDROM packet commands, door lock/eject/start/stop, host/device identification, SG timeout/reserved-size controls, and reset dispatch.

Important APIs/types/functions: `scsi_ioctl()` is the exported dispatcher. `sg_io()` builds a passthrough request from `struct sg_io_hdr`, maps userspace I/O with `blk_rq_map_user_io()`, executes it, and fills status/sense fields. `sg_scsi_ioctl()` implements the old page-limited ABI. `get_sg_io_hdr()` and `put_sg_io_hdr()` translate native and compat SG headers. `scsi_cmd_allowed()` enforces unprivileged command filtering. `scsi_set_medium_removal()` sends ALLOW MEDIUM REMOVAL and updates `sdev->locked`.

Control flow: the dispatcher warns on deprecated ioctls, handles generic SG commands directly, routes reset to `scsi_ioctl_reset()`, and falls back to low-level driver ioctl callbacks. SG_IO validates interface id, transfer direction, transfer size, command length, permissions, and timeout, allocates a SCSI request, maps userspace buffers, executes synchronously, records duration, copies sense data back, unmaps the bio, and frees the request. CDROM packet ioctl is converted into an SG_IO-like request.

State and persistence: ioctl calls mutate runtime fields such as `sdev->sg_timeout`, `sg_reserved_size`, `lockable`, `locked`, and `changed`. They may also trigger device-visible media removal, start/stop, eject, and reset operations. There is no local durable persistence.

Dependencies and integration: depends on blk-mq request allocation from `scsi_lib.c`, command execution helpers, sense printing, Linux user-copy/compat APIs, cdrom and sg ABI structs, capability checks in `scsi_cmd_allowed()`, and error-handler reset support.

Risks: this file is a security boundary because unprivileged users can submit a restricted subset of CDBs. Command allowlisting, write-open checks, compat pointer conversion, length validation, and sense copying are key. Deprecated ioctls have fixed command length and PAGE_SIZE data limits. This source snapshot shows duplicated lines around reserved size and the old ioctl declaration, which should be compile-tested.

Test signals: run SG_IO read-only and write commands as privileged and unprivileged users, compat 32-bit SG_IO/CDROM paths, invalid command lengths and directions, oversize transfers, sense-buffer copyout, deprecated ioctl warning paths, door lock/unlock on removable media, reset permission failures, and driver ioctl fallback.
