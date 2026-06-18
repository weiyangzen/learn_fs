# sources/distributed-fs/ceph-client/drivers/nvme/host/ioctl.c

## Purpose
This file implements the userspace command submission surface for NVMe block devices, namespace character devices, namespace-head multipath character/block devices, and controller character devices. It supports legacy ioctls (`NVME_IOCTL_*`) and `io_uring_cmd` passthrough for admin and I/O commands, including vectored and fixed-buffer paths, metadata mapping, polling, and nonblocking request allocation.

## Important APIs, Types, And Functions
Public entry points are `nvme_ioctl()`, `nvme_ns_chr_ioctl()`, `nvme_ns_chr_uring_cmd()`, `nvme_ns_chr_uring_cmd_iopoll()`, `nvme_ns_head_ioctl()`, `nvme_ns_head_chr_ioctl()`, `nvme_ns_head_chr_uring_cmd()`, `nvme_dev_uring_cmd()`, and `nvme_dev_ioctl()`. The file also handles deprecated controller-char `NVME_IOCTL_IO_CMD` through `nvme_dev_user_cmd()`.

Permission and setup helpers include `nvme_cmd_allowed()`, `nvme_to_user_ptr()`, `nvme_alloc_user_request()`, `nvme_map_user_request()`, `nvme_submit_user_cmd()`, `nvme_submit_io()`, `nvme_validate_passthru_nsid()`, `nvme_user_cmd()`, and `nvme_user_cmd64()`. `struct nvme_uring_data` snapshots user command fields, and `struct nvme_uring_cmd_pdu` stores request, bio, result, and status in the io_uring command private data.

## Control Flow
Legacy namespace ioctls dispatch through `nvme_ns_ioctl()`. `NVME_IOCTL_ID` returns the namespace ID. `NVME_IOCTL_SUBMIT_IO` copies `struct nvme_user_io`, validates read/write/compare opcodes, computes data and metadata lengths from namespace format, handles protection information and extended LBA cases, builds an NVMe read/write command, and submits it synchronously. Passthrough ioctls copy 32-bit or 64-bit passthrough structures, validate namespace ID, construct `struct nvme_command`, check permissions, map user data and metadata, execute the request, unmap the bio, and copy the result back to userspace.

`nvme_cmd_allowed()` is the main security gate. It allows only safe unprivileged commands: no partition escape, no vendor/fabrics commands, only a small admin identify subset without a namespace, and only I/O commands that the Command Effects log marks supported and not intrusive. Writes or logical-block-content-changing commands require the file to be open for write. Otherwise `CAP_SYS_ADMIN` is required.

`io_uring_cmd` flow starts with `nvme_uring_cmd_checks()`, requiring 128-byte SQEs and 32-byte CQEs. `nvme_uring_cmd_io()` snapshots command fields with `READ_ONCE()`, validates flags and nsid, applies the same permission policy, imports fixed buffers when requested, sets `REQ_NOWAIT` or `REQ_POLLED` from issue flags, allocates a request, maps data and metadata, stores the bio for later unmap, installs `nvme_uring_cmd_end_io()`, and submits with `blk_execute_rq_nowait()`. Completion either finishes inline for matching IOPOLL context or posts task work so completion runs in the owning io_uring context.

Multipath namespace-head ioctls select a live path under `head->srcu` with `nvme_find_path()`. Controller-level ioctls deliberately drop the namespace-head SRCU reference early after taking a controller reference to avoid deadlocks when passthrough deletes namespaces.

## State And Persistence
This file does not create persistent device state, but it mutates controller and namespace state through submitted admin/I/O commands and through controller management ioctls such as reset, subsystem reset, and rescan. Per-request state lives in blk-mq requests, mapped bios, request flags (`NVME_REQ_USERCMD`), optional metadata mappings, and io_uring PDU fields. For multipath, SRCU protects selected namespace paths during ioctl or io_uring submission.

Passthrough effects are bracketed by `nvme_passthru_start()` and `nvme_passthru_end()`, allowing command effects to trigger namespace/controller rescans, quiescing, or other core behavior after command completion.

## Dependencies And Integration Points
The file depends on Linux ioctl, block, blk-integrity, compat, ptrace syscall return, io_uring command, request mapping, and SED OPAL helpers. NVMe integration points include command setup/execution, command effects, namespace ID validation, namespace-head path selection, controller reset/rescan, metadata integrity mapping, and multipath SRCU.

It is wired into block-device operations, namespace character file operations, namespace-head file operations from `multipath.c`, and controller character-device operations declared in `nvme.h`.

## Risks
This is a high-risk userspace boundary. Incorrect permission checks could expose vendor/admin/fabrics commands, writes through read-only descriptors, or partition escape. Incorrect user pointer handling can break compat tasks; `nvme_to_user_ptr()` intentionally truncates upper bits for compat behavior. Metadata mapping must match namespace integrity support and extended LBA/PI rules or user buffers can be interpreted incorrectly.

io_uring adds lifetime risk because request completion may be inline, task-work based, polled, cancelled, or nonblocking. The PDU stores the bio because `req->bio` can be cleared by completion time; missing that unmap would leak user mappings. Multipath head controller ioctls must avoid holding SRCU across operations that delete namespaces, which is why `nvme_ns_head_ctrl_ioctl()` drops SRCU before calling controller ioctl.

## Test Signals
Test unprivileged and privileged passthrough for allowed identify commands, denied vendor/admin/fabrics commands, partition passthrough denial, write commands on read-only fds, command effects handling, metadata mapping with and without integrity, extended LBA namespaces, PRACT metadata stripping, compat `NVME_IOCTL_SUBMIT_IO32`, and result copyout failures.

io_uring tests should cover admin and I/O commands, vectored and non-vectored fixed buffers, `IO_URING_F_NONBLOCK`, `IO_URING_F_IOPOLL`, cancellation, inline poll completion, task-work completion, metadata buffers, invalid nsids, missing SQE128/CQE32 support, and multipath namespace-head path disappearance while commands are issued. Controller ioctl tests should cover reset, subsystem reset, rescan, SED ioctls, and deprecated char-device I/O passthrough with one versus multiple namespaces.
