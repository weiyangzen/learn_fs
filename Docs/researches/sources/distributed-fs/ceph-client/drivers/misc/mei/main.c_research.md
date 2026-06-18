<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/main.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/main.c

Purpose: implements the MEI character-device interface, sysfs attributes, minor allocation/registration, module initialization, and userspace-facing file operations for connecting to firmware clients and exchanging messages.

Important APIs and functions: file operations are `mei_open()`, `mei_release()`, `mei_read()`, `mei_write()`, `mei_ioctl()`, `mei_poll()`, `mei_fsync()`, and `mei_fasync()`. IOCTL helpers handle plain and vtagged connect, notification set/get, and vtag support checks. Sysfs attributes expose `fw_status`, `hbm_ver`, `hbm_ver_drv`, `tx_queue_limit`, `fw_ver`, `dev_state`, `trc`, and `kind`. Exported registration functions are `mei_register()`, `mei_deregister()`, and `mei_set_devstate()`.

Control flow: module init registers class, char-dev major range, and MEI client bus. Hardware probe calls `mei_register()` to allocate a minor, initialize/cdev/device, add sysfs groups, and register debugfs. `open` validates enabled state, allocates a linked `mei_cl`, and stores it in `file->private_data`. `ioctl` connects to a firmware UUID, optionally with vtags that share an existing connected client across file descriptors. `write` validates connection, MTU, activity, and tx queue limit before allocating a callback and queuing it. `read` starts a read callback if needed, waits unless nonblocking, copies completed callback data to userspace, and handles partial user reads through file offset. `poll` starts reads opportunistically and reports read/write/notification readiness.

State and persistence: global runtime state includes `mei_devt`, class, IDR of devices, minor lock, and per-device sysfs/cdev objects. Per-open state is `struct mei_cl` plus vtag mappings associated with file pointers. `tx_queue_limit` is mutable through sysfs but not persisted across reload/reboot.

Dependencies and integration: uses Linux char device APIs, IDR, sysfs, poll/fasync, runtime PM for FW status reads, MEI client/bus APIs, HBM version constants, and client queue helpers. Hardware backends register common MEI devices through this file.

Risks: file operations rely on `device_lock` for client and queue state. `release` may drop the lock during disconnect and must re-check vtag mappings afterward. Read/write paths must avoid sleeping while locked except through explicit unlock/wait/relock sections. Vtag sharing rejects duplicate or mismatched tags but has complex replacement logic. IOCTL copies can fail after connection state has changed, leaving a connected kernel client despite `-EFAULT`.

Test signals: `/dev/mei*` open/connect/read/write with blocking and nonblocking I/O, ioctl ABI tests for vtag and notification commands, poll/epoll readiness, sysfs attribute reads/writes, concurrent open/release with vtags, device deregistration while files are open, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/main.c -->
