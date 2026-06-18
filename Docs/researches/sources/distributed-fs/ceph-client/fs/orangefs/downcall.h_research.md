## sources/distributed-fs/ceph-client/fs/orangefs/downcall.h

### Purpose
This header defines the daemon-to-kernel response payloads for OrangeFS operations.

### Important APIs, types, and functions
- Response structs cover file I/O, lookup, create, symlink, getattr, mkdir, statfs, fs mount, xattrs, parameters, perf counters, fs keys, and features.
- `struct orangefs_downcall_s` contains `type`, `status`, optional trailer metadata, and a union of response payloads.
- `struct orangefs_readdir_response_s` defines the header at the start of readdir trailer data.

### Control flow
The daemon writes a downcall through `/dev/pvfs2-req`; `devorangefs-req.c` copies this struct into the waiting operation, then consuming subsystems read the matching union member after `service_operation()` returns.

### State and persistence behavior
The header is an in-memory protocol contract. `trailer_buf` is a kernel pointer allocated during write handling for readdir and later owned by directory iteration code.

### Dependencies and integration points
Included by `orangefs-dev-proto.h`, paired with `upcall.h`, and consumed by file, inode, superblock, directory, xattr, sysfs, and debug code. Sizes and field alignment are part of the kernel/userspace ABI.

### Risks
The structs carry fixed-size arrays and 32/64-bit fields, so padding and compatibility matter. The comment notes readdir response data lives in the trailer, making trailer size validation critical. Any ABI change must preserve userspace daemon compatibility.

### Test signals
Protocol tests should validate 32-bit and 64-bit daemon interaction, each operation type's expected response union, readdir trailer parsing, and behavior for nonzero `status`.
