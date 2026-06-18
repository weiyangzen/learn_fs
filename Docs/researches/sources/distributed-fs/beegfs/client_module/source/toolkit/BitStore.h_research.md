## sources/distributed-fs/beegfs/client_module/source/toolkit/BitStore.h

**Purpose:** Declares the `BitStore` bit-vector structure and inline helpers for construction, destruction, bit lookup, and bit-index arithmetic.

**Important APIs/types/functions:** Defines `bitstore_store_type`, block-size constants, `struct BitStore`, inline `BitStore_init`, `initWithSizeAndReset`, `uninit`, `getBit`, `getBitBlockIndex`, `getBitIndexInBitBlock`, and `calculateBitBlockCount`, plus external mutating/serialization functions.

**Control flow:** Callers initialize with a default one-block capacity, optionally resize/reset, perform atomic bit lookups via `test_bit`, and uninitialize optional heap storage.

**State and persistence behavior:** Stores a rounded capacity in `numBits`, one inline lower block, and optional heap-backed higher blocks. The header's inline `getBit` treats out-of-range reads as false.

**Dependencies and integration points:** Used anywhere compact dynamic bitsets are needed, notably `RemotingIOInfo.firstWriteDone`. Depends on BeeGFS common macros and serialization types.

**Risks:** `BitStore_init(this, false)` leaves `lowerBits` uninitialized until callers clear or deserialize. `BitStore_uninit` frees `higherBits` without nulling, so destroyed objects must not be reused without reinit. The block type is machine word sized, so serialized compatibility relies on `.c` conversion logic.

**Test signals:** Build with debug bug macros, test initialized-without-clear paths for callers, validate block index math around word boundaries, and run leak/use-after-free checks for init/uninit cycles.
