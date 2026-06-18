<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/LockingTk.h -->
## sources/distributed-fs/beegfs/client_module/source/common/toolkit/LockingTk.h

**Purpose:** Converts entry-lock flag combinations to stable human-readable strings for logs/debugging. **APIs/functions:** inline `LockingTk_lockTypeToStr`. **Control flow:** first checks `ENTRYLOCKTYPE_NOWAIT`, then returns unlock/exclusive/shared/unknown variants with `|nowait` or `|wait`. **State/persistence:** no state; strings are static literals. **Dependencies/integration:** uses lock flag constants from `StorageDefinitions.h`. **Risks/tests:** combinations with multiple lock operation bits return the first priority branch; tests should cover all primary flags with and without NOWAIT and unknown combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/LockingTk.h -->
