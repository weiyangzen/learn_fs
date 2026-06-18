# sources/distributed-fs/ceph-client/fs/coda/psdev.c

Purpose: provides the Coda pseudo-device character driver and module init/exit path. It creates `/dev/cfsN`-style endpoints that Venus opens to exchange bidirectional upcall/downcall messages with kernel Coda VFS code.

Important APIs/types/functions: global `coda_comms[MAX_CODADEVS]` stores per-minor queues, waitqueue, sequence number, superblock pointer, and mutex. `coda_psdev_open()` initializes one `venus_comm` slot and restricts access to the initial PID/user namespaces. `coda_psdev_read()` moves queued kernel upcalls from `vc_pending` to userspace and, for synchronous requests, onto `vc_processing`. `coda_psdev_write()` receives Venus replies or downcalls, matches replies by unique id, copies output into the request buffer, converts `CODA_OPEN_BY_FD` descriptors with `fget()`, and wakes sleepers. `coda_psdev_release()` aborts and wakes all outstanding requests.

Control flow: module init creates the inode cache, registers the char major, creates device nodes, registers sysctls, then registers the Coda filesystem. Kernel VFS operations enqueue `upc_req`s through `coda_upcall()`; Venus polls/reads pending requests; Venus writes replies or invalidation downcalls; waiters resume or cache invalidation executes.

State and persistence: in-memory queues `vc_pending` and `vc_processing` persist while Venus holds the device. No on-disk state is stored here. `vc_inuse` enforces one opener per minor.

Dependencies/integration: integrates char-device VFS, poll, copy_to/from_user, device class creation, module lifecycle, Coda sysctls, Coda filesystem registration, and `coda_downcall()` in `upcall.c`.

Risks: request queue manipulation must be under `vc_mutex`; mismatched unique ids return `-ESRCH`. `CODA_OPEN_BY_FD` takes file references that later file code must release. Release must wake every blocked upcall or callers can hang. Namespace checks are important because the protocol uses initial namespace pid/uid values.

Test signals: concurrent read/write/poll behavior, nonblocking read, interrupted read, Venus reply after signal, downcall size validation, device open exclusivity, release with pending and processing requests, module load/unload cleanup, and `CIOC_KERNEL_VERSION` ioctl.
