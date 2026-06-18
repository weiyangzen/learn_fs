<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Random.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/Random.h

**Purpose:** Small per-instance pseudo-random helper based on `rand_r`, used for non-cryptographic jitter and random test data.

**Important APIs/types/functions:** Constructors seed from current `timeval.tv_usec` or explicit seed. `getNextInt` returns a non-negative integer. `getNextInRange(min, max)` returns an inclusive bounded value using modulo reduction.

**Control flow:** Each call invokes `rand_r(&seed)`, normalizes negative results with bitwise complement, and updates the internal seed. Range selection uses `% (max - min + 1)` and adds `min`.

**State and persistence behavior:** Holds one mutable unsigned seed in memory. No persistent state.

**Dependencies and integration points:** Depends on BeeGFS common headers for system includes. Used by retry jitter, string generation, and tests such as `TestBitStore` and `TestRWLock`.

**Risks:** Not cryptographically secure, not statistically ideal due to modulo bias, and not thread-safe if the same instance is shared. `getNextInRange` assumes `max >= min` and can divide by zero or overflow otherwise.

**Test signals:** Indirectly exercised by randomized tests and retry helpers. Deterministic explicit-seed tests would be useful for range boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Random.h -->
