<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/system/System.c -->
## sources/distributed-fs/beegfs/client_module/source/common/system/System.c

**Purpose:** Provides a kernel-module helper to copy the current hostname. **APIs/functions:** `System_getHostnameCopy`. **Control flow:** chooses `system_utsname.nodename` or `utsname()->nodename` depending on kernel feature macros, uses `uts_sem` only for very old kernels, allocates a copy with `kmalloc`, and returns NULL on allocation failure. **State/persistence:** reads transient kernel UTS state and returns caller-owned memory. **Dependencies/integration:** used wherever the client needs a node/host alias seed. **Risks/tests:** comments note racy access on newer kernels after `uts_sem` became unavailable; tests should cover allocation failure handling and compile paths across kernel versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/system/System.c -->
