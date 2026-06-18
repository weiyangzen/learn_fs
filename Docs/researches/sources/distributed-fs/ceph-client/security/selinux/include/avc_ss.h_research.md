## sources/distributed-fs/ceph-client/security/selinux/include/avc_ss.h

### Purpose
`avc_ss.h` is the security-server-facing AVC interface. It exposes AVC reset support and the class/permission mapping table needed by the security server and generated header tools.

### Important APIs, types, and functions
It declares `avc_ss_reset(u32 seqno)` and `struct security_class_mapping`, whose `name` identifies a class and whose `perms` array contains up to 32 permission names plus a null terminator. It also declares `extern const struct security_class_mapping secclass_map[]`.

### Control flow
The security server calls `avc_ss_reset()` with a policy sequence number when policy state changes. Mapping consumers iterate `secclass_map[]` until the null class entry.

### State and persistence
No state is stored in the header. The mapping table is defined by `classmap.h`, and reset state is maintained by the AVC implementation.

### Dependencies and integration points
This header bridges `classmap.h`, `genheaders.c`, `avc.c`, `services.c`, and `hooks.c` logging paths that need class names.

### Risks
The table shape is ABI-like within the SELinux build. Class ordering and permission ordering must match generated constants and policy expectations.

### Test signals
Regenerate and build SELinux Flask headers; load policy; trigger policy reload and confirm AVC reset and class-name audit formatting continue to work.
