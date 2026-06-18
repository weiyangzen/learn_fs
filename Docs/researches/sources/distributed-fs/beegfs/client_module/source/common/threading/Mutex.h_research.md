<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/threading/Mutex.h -->
## sources/distributed-fs/beegfs/client_module/source/common/threading/Mutex.h

**Purpose:** Thin wrapper around Linux `struct mutex`. **APIs/types:** `Mutex` stores a kernel mutex with inline init, uninit/destroy, lock, and unlock. **Control flow/state:** no extra ownership or debugging beyond kernel mutex APIs. **Dependencies/integration:** used across node, connection, thread, and condition code. **Risks/tests:** all blocking behavior is kernel mutex behavior; tests should focus on correct pairing and not using after uninit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/threading/Mutex.h -->
