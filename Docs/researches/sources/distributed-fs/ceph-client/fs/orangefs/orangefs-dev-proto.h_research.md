## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-dev-proto.h

### Purpose
This header defines operation type constants and shared protocol limits for the OrangeFS kernel/userspace device ABI.

### Important APIs, types, and functions
- `ORANGEFS_VFS_OP_*` constants enumerate file I/O, lookup, create, metadata, mount, xattr, parameter, perf, cancel, fsync, fs key, readdirplus, and feature requests.
- `ORANGEFS_FEATURE_READAHEAD` declares the negotiated readahead feature bit.
- `ORANGEFS_MAX_DEBUG_STRING_LEN` and `ORANGEFS_MAX_DIRENT_COUNT_READDIR` set fixed protocol buffer limits.
- It includes `upcall.h` and `downcall.h`.

### Control flow
Operation allocation sets one of these op types in `upcall.type`; the daemon receives that type and returns a matching downcall type/status. Feature negotiation and sysfs support use the readahead feature flag.

### State and persistence behavior
No runtime state. The constants are a stable ABI shared by kernel and daemon.

### Dependencies and integration points
Included by `orangefs-kernel.h` and thus almost every OrangeFS file. The fixed constants must match userspace client-core definitions.

### Risks
ABI drift between kernel and daemon would break operation dispatch. The comment warns constants should remain multiples of 8 where relevant to avoid 32/64-bit interaction issues.

### Test signals
Run protocol compatibility tests across 32-bit compat and native userspace, daemon/kernel version mismatch tests, and feature negotiation tests for readahead support.
