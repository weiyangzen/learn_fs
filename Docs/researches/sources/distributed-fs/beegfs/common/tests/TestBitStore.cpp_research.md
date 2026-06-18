<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestBitStore.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestBitStore.cpp

**Purpose:** GoogleTest coverage for `BitStore` sizing, bit access, mutation, clearing, and serialization.

**Important APIs/types/functions:** Fixture `TestBitStore` exposes private `lowerBits` and `higherBits`. Tests include `calculateBitBlockCount`, `setSizeAndReset`, `getter`, `setter`, helper `checkSerialization`, and `serialization`.

**Control flow:** Block-count tests iterate sizes up to 242 and compare expected limb counts. Getter/setter tests set one bit at a time, inspect the exact lower/higher limb values, and clear between iterations. Serialization computes size with a sizing serializer, writes to a buffer, deserializes into a second `BitStore`, checks `good`, byte consumption, and equality. Random-value serialization sets 75 random bits.

**State and persistence behavior:** Test-only in-memory state. It validates `BitStore` binary serialization compatibility through the common serializer.

**Dependencies and integration points:** Depends on `BitStore`, `Random`, `Serialization`, Boost scoped arrays, and GoogleTest. It is a direct test signal for `Serialization.h`.

**Risks:** `setSizeAndReset` has `bool finished = false; while(finished)` and therefore never executes, leaving intended resize/reset coverage disabled by a logic bug. Random test is nondeterministic. Private-field access in the fixture couples tests to implementation layout.

**Test signals:** Existing active tests cover block count, single-bit getter/setter, and serialization. Fixing the loop would restore reset coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestBitStore.cpp -->
