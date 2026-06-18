<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BitStore.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/BitStore.h

Purpose: Declares a serializable bit vector optimized for small stores.

Important APIs/types: `BitStore` exposes constructors, `init`, `setBit`, `getBitNonAtomic`, `setSize`, `clearBits`, serialization, equality, assignment, and `calculateBitBlockCount`.

Control flow/state/persistence: State consists of bit count, low block, and optional heap-allocated higher blocks. It is not thread-safe; callers synchronize externally.

Dependencies/integration: Used by message/config structures needing dense boolean sets.

Risks/test signals: Bounds checking is caller-limited. Tests should verify out-of-range behavior expected by callers, allocation transitions, and copy/assignment independence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BitStore.h -->
