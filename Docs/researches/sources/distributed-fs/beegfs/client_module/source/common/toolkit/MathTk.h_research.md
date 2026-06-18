<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/MathTk.h -->
## sources/distributed-fs/beegfs/client_module/source/common/toolkit/MathTk.h

**Purpose:** Provides small math helpers used by kernel-client code. **APIs/functions:** `MathTk_log2Int32` and `MathTk_isPowerOfTwo`. **Control flow:** log2 uses `__builtin_clz` and is undefined for zero; power-of-two uses the classic `!(value & (value - 1))` expression and is also documented as undefined for zero, though it returns true for zero in C. **State/persistence:** none. **Dependencies/integration:** used by code that assumes power-of-two chunk sizes and similar bit-level optimizations. **Risks/tests:** zero handling is a sharp edge; tests should explicitly reject zero before calling these helpers and verify powers/non-powers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/MathTk.h -->
