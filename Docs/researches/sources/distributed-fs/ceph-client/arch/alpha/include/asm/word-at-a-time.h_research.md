<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/word-at-a-time.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/word-at-a-time.h

**Purpose:** Implements Alpha word-at-a-time zero-byte detection for optimized string routines.

**Important APIs/types/functions:** `struct word_at_a_time`, `WORD_AT_A_TIME_CONSTANTS`, `has_zero`, `prep_zero_mask`, `create_zero_mask`, `find_zero`, and `zero_bytemask`.

**Control flow:** `has_zero` uses Alpha `cmpbge` helper to identify zero-byte positions. `find_zero` uses CIX count-trailing-zero where available or a small bit search fallback.

**State and persistence behavior:** No state.

**Dependencies and integration points:** Depends on Alpha compiler helpers `__kernel_cmpbge` and optionally `__kernel_cttz`, plus generic word-at-a-time string code.

**Risks:** Byte-position masks are endian/architecture-specific. Wrong `find_zero` mapping corrupts string length/copy termination.

**Test signals:** String tests for NUL at every byte position, CIX and non-CIX builds, and unaligned string workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/word-at-a-time.h -->
