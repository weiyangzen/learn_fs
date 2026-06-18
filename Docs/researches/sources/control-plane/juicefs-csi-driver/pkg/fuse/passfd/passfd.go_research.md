# sources/control-plane/juicefs-csi-driver/pkg/fuse/passfd/passfd.go

Purpose: manages FUSE file descriptor discovery, storage, serving, and transfer across mount pod graceful upgrades using Unix domain sockets and ancillary file descriptor passing.

Important APIs and types: `Fds` owns a Kubernetes client, mutex, base path, and map from upgrade UUID to `fd` records. Global entry points include `InitGlobalFds`, `InitTestFds`, `GetFdAddress`, and `GlobalFds`. Methods include `PrintFds`, `ParseFuseFds`, `getFdAddress`, `StopFd`, `CloseFd`, `parseFuse`, `ServeFuseFd`, `serveFuseFD`, `handleFDRequest`, `UpdateSid`, and `GetSid`. Low-level helpers `GetFuseFd`, `getFd`, and `putFd` receive/send Unix file descriptors.

Control flow: initialization creates a global registry and asynchronously scans the base path for `fuse_fd_comm.*` sockets belonging to live eligible mount pods. `getFdAddress` allocates a per-upgrade socket path if no fd is known. `parseFuse` connects to an existing pod socket to receive the FUSE fd, stores it, and starts a server socket. `handleFDRequest` sends the saved fd and setting to a requester, closes local ownership, then receives a replacement fd or close message. `StopFd` and `CloseFd` clean up descriptors and socket directories.

State and persistence behavior: process-local state is guarded by `globalMu` and includes fd integers, fuse settings, session IDs, and socket paths. Filesystem state includes per-upgrade directories and Unix socket files under `basePath`. Kernel fd ownership is actively transferred and closed, so incorrect sequencing can leak or prematurely close FUSE fds.

Dependencies and integration points: integrates Kubernetes pod listing/labels, upgrade UUID helpers, global graceful-upgrade config, mount path existence checks, Unix sockets, `syscall.Sendmsg`/`Recvmsg`, `SCM_RIGHTS`, and `config.SupportFusePass`.

Risks and test signals: `ParseFuseFds` launches goroutines that capture loop variables (`entry` and `subdir`); under older Go versions this could target the wrong directory. `getFd` assumes rights parsing succeeds and may append nil/empty rights before checking errors. Socket server goroutines rely on `done` closure and listener close behavior. No listed tests cover fd transfer, so this path is high-risk and integration-dependent.
