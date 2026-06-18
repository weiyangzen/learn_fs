# sources/distributed-fs/ceph-client/include/linux/errno.h

Purpose: internal kernel errno extensions beyond UAPI errno values.

Important APIs/types/functions: restart/internal codes `ERESTARTSYS`, `ERESTARTNOINTR`, `ERESTARTNOHAND`, `ERESTART_RESTARTBLOCK`, probe/open/ioctl codes such as `ENOIOCTLCMD`, `EPROBE_DEFER`, `EOPENSTALE`, `ENOPARAM`, NFS/internal network filesystem codes, `EIOCBQUEUED`, `ERECALLCONFLICT`, and `ENOGRACE`.

Control flow: syscalls and subsystems return these internal negative errors; VFS/syscall exit, signal restart logic, driver core, NFS, and AIO convert or consume them before exposing user-visible errno.

State/persistence: no state; values are ABI-sensitive internal constants.

Dependencies/integration: UAPI asm errno, syscall restart machinery, driver probing, NFS/exportfs, VFS open, async I/O.

Risks/test signals: risks are leaking internal restart codes to userspace, numeric collisions, and mishandling `EPROBE_DEFER` or queued AIO. Test syscall interruption/restart, deferred probe, stale open retry, NFS error translation, and ioctl unknown-command paths.
