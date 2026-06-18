# sources/distributed-fs/ceph-client/kernel/liveupdate/luo_core.c

## Purpose
`luo_core.c` implements the Live Update Orchestrator entry points, boot-time FDT setup/retrieval, global enable state, reboot serialization hook, and `/dev/liveupdate` control device. It coordinates LUO sessions and file lifecycle-bound global data on top of KHO subtrees.

## Important APIs, Types, and Functions
Global state is `luo_global` with `enabled`, outgoing/incoming FDT pointers, and `liveupdate_num`, plus exported `luo_register_rwlock` for handler/FLB registration. Early/late init functions are `liveupdate_early_init()`, `luo_early_startup()`, `luo_late_startup()`, and `luo_fdt_setup()`. Public runtime functions are `liveupdate_reboot()` and `liveupdate_enabled()`.

The control device uses `struct luo_device_state`, `luo_open()`, `luo_release()`, `luo_ioctl()`, and ioctl handlers `luo_ioctl_create_session()` and `luo_ioctl_retrieve_session()`. It registers a misc device named `liveupdate`.

## Control Flow
The `liveupdate=` early parameter controls `luo_global.enabled`; KHO disablement forces LUO off. Early init tries to retrieve the LUO subtree from KHO. If present, it validates the LUO FDT compatible string, loads the liveupdate counter, and sets up incoming session and FLB headers. A failure in incoming restore panics through `luo_restore_fail()` because the preserved state may be inconsistent.

Late init prepares an outgoing LUO FDT when liveupdate is enabled. It allocates preserved FDT memory, writes compatible and incremented liveupdate number properties, adds session and FLB nodes, finalizes the FDT, and registers it as a KHO subtree.

Userspace opens `/dev/liveupdate` exclusively. Open triggers one-time session deserialization, so incoming sessions become available only when the controller starts. Ioctls create new outgoing sessions or retrieve named incoming sessions and return file descriptors.

On kexec reboot, `liveupdate_reboot()` serializes all outgoing sessions; if successful, it serializes FLB metadata. Errors abort reboot before KHO finalization.

## State and Persistence Behavior
LUO persists a dedicated FDT subtree through KHO, including a monotonic liveupdate number, session header pointer, and FLB header pointer. Runtime state includes incoming/outgoing FDT pointers, an exclusive-open flag, session lists, file handlers, FLBs, and preserved KHO allocations. `/dev/liveupdate` is singleton to avoid conflicting userspace controllers.

## Dependencies and Integration Points
It depends on KHO subtree APIs, libfdt, miscdevice/file descriptor APIs, UAPI liveupdate ioctls, session and FLB modules, and reboot/kexec integration through `liveupdate_reboot()`. File handler registration across LUO modules is serialized by `luo_register_rwlock`.

## Risks and Test Signals
Incoming FDT corruption is treated as fatal; tests must validate panic paths only in controlled environments. Ioctl size negotiation uses `copy_struct_from_user()` and minimum field offsets; ABI changes must preserve compatibility. Exclusive open prevents races but also serializes deserialization failures into `-EIO`. Tests should cover `liveupdate=on/off`, KHO disabled, cold boot with no subtree, incoming subtree validation, create/retrieve session ioctls, open exclusivity, and reboot serialization rollback.
