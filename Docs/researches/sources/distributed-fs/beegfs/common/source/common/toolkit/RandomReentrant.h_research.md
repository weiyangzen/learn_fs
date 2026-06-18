<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/RandomReentrant.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/RandomReentrant.h

**Purpose:** Variant of `Random` intended to reduce duplicate seeds under concurrent use without full locking or atomic synchronization.

**Important APIs/types/functions:** Constructors seed from microseconds or explicit seed. `getNextInt` copies and increments a volatile seed, calls `rand_r`, writes back the updated temporary seed, and normalizes negative results. `getNextInRange` mirrors `Random`.

**Control flow:** The seed pre-increment is intended to make simultaneous threads less likely to feed the same seed to `rand_r`. It is best-effort only.

**State and persistence behavior:** Maintains a volatile unsigned seed in memory. No persistence and no synchronization guarantees.

**Dependencies and integration points:** Shared utility for places that want cheap random values from multiple threads without a mutex. Its comment explicitly limits the reentrancy claim.

**Risks:** `volatile` does not make updates atomic or race-free in C++. Concurrent access can still lose updates and is technically data-racy. Like `Random`, it is not cryptographic and range selection is modulo-biased.

**Test signals:** No direct tests. Multithreaded tests should avoid assuming deterministic behavior and should focus on absence of crashes plus valid range bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/RandomReentrant.h -->
