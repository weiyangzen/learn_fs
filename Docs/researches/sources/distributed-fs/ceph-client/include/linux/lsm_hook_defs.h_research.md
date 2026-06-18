<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_hook_defs.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm_hook_defs.h

## Purpose
This header is the authoritative X-macro list of LSM hooks. It is included with different `LSM_HOOK` definitions to generate hook function pointer unions, static-call tables, dispatch code, and defaults.

## Important APIs, Types, and Functions
Each `LSM_HOOK(return_type, default, name, args...)` entry defines one security hook. The file covers filesystem, path, inode, file, task, credentials, IPC, key, network, XFRM, BPF, audit, io_uring, perf, lockdown, notification, block-device, and initramfs hooks. Defaults encode allow, deny, unsupported, or void behavior.

## Control Flow
There is no direct control flow. Generated callers use this list to invoke registered LSM callbacks in stacking order, applying the per-hook default when no module handles a hook or when a hook family is disabled.

## State and Persistence Behavior
The header owns no state. It shapes generated runtime hook lists and static-call slots in the security framework.

## Dependencies and Integration Points
It is included by `lsm_hooks.h` and security implementation files with a caller-defined `LSM_HOOK` macro. It depends on many forward-declared kernel types being visible at include sites.

## Risks and Test Signals
Risks include prototype drift, wrong default return values, missing conditional guards for optional subsystems, and breaking all generated users of a hook. Test signals are full security Kconfig builds, LSM selftests, hook registration tests, and behavior checks for unsupported/default hook paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_hook_defs.h -->
