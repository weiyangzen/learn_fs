<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ListTk.h -->
## sources/distributed-fs/beegfs/client_module/source/common/toolkit/ListTk.h

**Purpose:** Declares shared list helper functions. **APIs/types:** externs clone and sorted-clone NIC address lists, copy UInt16 list contents into a vector, free NIC/NIC-stats list elements, and search string-copy lists with an output position. **Control flow/state:** function contracts separate element ownership from list container lifetime. **Dependencies/integration:** includes NIC lists, stats lists, filters, string lists, and UInt16 list/vector types. **Risks/tests:** callers must uninitialize containers after freeing elements; tests should verify no shallow-copy aliasing in cloned NIC lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ListTk.h -->
