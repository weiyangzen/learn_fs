
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bsg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/bsg.h

## Purpose
Defines the block SCSI generic v4 userspace command ABI used by `/dev/bsg/*` and io_uring passthrough. It carries protocol identifiers, command/request pointers, data buffers, sense data, status fields, and packed helpers for io_uring SCSI result reporting.

## APIs, Control Flow, and State
`struct sg_io_v4` is the main ioctl payload. It includes guard/protocol/subprotocol fields, request and response lengths, user pointers, bidirectional data-transfer pointers and lengths, timeout/flags, device/transport/driver status, residual count, duration, and generated tag. `struct bsg_uring_cmd` is the io_uring variant with request buffer, data/sense addresses, lengths, timeout, flags, and `usr_ptr`. The header also defines queue-placement flags and inline helpers to unpack/build `res2` status fields: device status, driver status, host status, sense length, residual length, and combined builder. Control flow is external in bsg, SCSI, and io_uring command dispatch; this header only fixes ABI layouts. Persistent state is in device queues, pending commands, and user buffers referenced by the structures.

## Dependencies, Integration, Risks, and Tests
Depends on Linux integer types and kernel-only build assertions for structure size. Integration points are SCSI generic passthrough, block transport management, bsg char devices, and io_uring command completion. Risks include user pointer validation, 32/64-bit ABI compatibility, unchecked response/sense lengths, status packing mistakes in `res2`, and exposing transport commands to callers with insufficient permissions. Test signals include sg3_utils passthrough tests, bsg transport management commands, io_uring passthrough completion-status tests, compat syscall tests, and fuzzing of lengths, flags, and timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bsg.h -->
