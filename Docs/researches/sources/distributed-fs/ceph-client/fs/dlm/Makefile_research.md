<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/Makefile -->
# sources/distributed-fs/ceph-client/fs/dlm/Makefile

Purpose: defines the composite object list for the kernel Distributed Lock Manager.

Important APIs/types/functions: `obj-$(CONFIG_DLM) += dlm.o`; `dlm-y` includes callback, config, directory, lock, lockspace, main, member, memory, mid/low comms, plock, recovery, request queue, user, and utility objects; `dlm-$(CONFIG_DLM_DEBUG) += debug_fs.o`.

Control flow: Kbuild links all core DLM objects into `dlm.o` when `CONFIG_DLM` is enabled, with `debug_fs.o` conditionally included for debugfs diagnostics.

State and persistence: no runtime state directly, but the object list determines whether DLM includes configfs, networking, recovery, userspace device, and debug functionality.

Dependencies and integration: coordinates all DLM implementation files in this directory and mirrors the Kconfig debug split.

Risks: missing an object can produce unresolved symbols or silently remove a subsystem path such as recovery or user AST delivery. Conditional debug object inclusion must match header stubs in `dlm_internal.h`.

Test signals: full DLM build, module link, and debug-enabled builds should compile cleanly; symbol resolution across DLM components is the primary check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/Makefile -->
