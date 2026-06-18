# sources/distributed-fs/ceph-client/fs/xfs/xfs_notify_failure.h

Purpose: Declares the XFS DAX holder operations object used to receive media failure notifications from DAX devices.

Important APIs, types, and functions: Exposes `extern const struct dax_holder_operations xfs_dax_holder_operations`.

Control flow: Consumers include this header and register the operations with DAX-capable buffer targets. The actual callback implementation lives in `xfs_notify_failure.c`.

State and persistence behavior: No state is stored in the header. Runtime effects are entirely in the registered operations.

Dependencies and integration points: Relies on Linux `struct dax_holder_operations` being visible to includers. It is integrated by the buffer target setup path for DAX devices.

Risks: If the operations object is not registered for a DAX target, media failure callbacks will not reach XFS. Header changes should remain minimal to avoid leaking implementation details.

Test signals: Build DAX-enabled configurations and confirm `xfs_buf.c` references the exported object; trigger a synthetic DAX notify path and observe dispatch into XFS.
