<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/system/System.h -->
## sources/distributed-fs/beegfs/client_module/source/common/system/System.h

**Purpose:** Declares the hostname copy helper. **APIs/types:** `System_getHostnameCopy` returns a newly allocated hostname string. **Control flow/state:** no inline logic; caller owns the returned allocation. **Dependencies/integration:** includes `Common.h` for kernel/common definitions. **Risks/tests:** callers must free non-NULL results and handle NULL on allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/system/System.h -->
