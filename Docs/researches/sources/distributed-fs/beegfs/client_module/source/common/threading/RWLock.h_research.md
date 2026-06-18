<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/threading/RWLock.h -->
## sources/distributed-fs/beegfs/client_module/source/common/threading/RWLock.h

**Purpose:** Thin wrapper around Linux read/write semaphores. **APIs/types:** `RWLock` stores `rw_semaphore`; inline init, write lock, write trylock, read lock, write unlock, and read unlock. **Control flow/state:** callers choose read vs write exclusion; trylock returns the kernel `down_write_trylock` result. **Dependencies/integration:** protects node aliases, target mappings, mirror groups, and target states. **Risks/tests:** lock ordering is external and important for state/group sync; tests should cover trylock failure and no read-to-write upgrade assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/threading/RWLock.h -->
