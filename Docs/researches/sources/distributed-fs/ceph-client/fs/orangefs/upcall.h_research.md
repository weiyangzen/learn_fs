## sources/distributed-fs/ceph-client/fs/orangefs/upcall.h

Purpose: this header defines the request side of the OrangeFS kernel-to-userspace upcall ABI. Each `orangefs_*_request_s` structure describes the fixed wire payload for a VFS operation that will be queued to the client-core.

Important APIs and types: request structures cover file I/O, lookup, create, symlink, getattr, setattr, remove, mkdir, readdir/readdirplus, rename, statfs, truncate, readahead flush, mount/unmount, get/set/list/remove xattr, cancel, fsync, parameter get/set, performance counters, fs key lookup, and features negotiation. `struct orangefs_upcall_s` wraps common `type`, `uid`, `gid`, `pid`, `tgid`, trailer fields, and a union of all request payloads. `enum orangefs_param_request_type`, `enum orangefs_param_request_op`, and `enum orangefs_perf_count_request_type` enumerate tunable and counter operations.

Control flow: the header has no executable flow, but every `op_alloc(type)` user fills the matching member of `orangefs_upcall_s::req` before `service_operation()` queues the operation. `service_operation()` also fills `pid` and `tgid`; callers often fill credentials (`uid`, `gid`) and object references.

State and persistence behavior: upcall instances are transient operation state. Fixed-width fields and explicit pads preserve kernel/userspace ABI stability, especially for 32/64-bit interaction. The union design means only the request matching `type` is valid for a given op.

Dependencies and integration points: depends on protocol definitions such as `orangefs_object_kref`, `ORANGEFS_sys_attr_s`, `ORANGEFS_keyval_pair`, xattr limits, and I/O enums. It is paired with downcall structures in device protocol headers and consumed by waitqueue/device code and all OrangeFS VFS operation implementations.

Risks and test signals: union member mismatches or missing fsid/ref fields cause userspace to operate on the wrong object or fail decoding. Fixed string arrays require careful `strscpy()` and length fields; xattr and symlink limits must match userspace. Tests should validate struct sizes/offsets, operation-specific field population, cancellation tag handling, 32-bit compat layout, and version-gated `features` negotiation.
