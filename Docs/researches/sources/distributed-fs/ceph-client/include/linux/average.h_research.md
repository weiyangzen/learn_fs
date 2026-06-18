# sources/distributed-fs/ceph-client/include/linux/average.h

## Purpose
Provides `DECLARE_EWMA()`, a macro for declaring fixed-precision exponentially weighted moving average helpers. It lets kernel code define compact, type-specific EWMA state and inline operations with compile-time precision and decay parameters.

## Important APIs, Types, And Functions
`DECLARE_EWMA(name, _precision, _weight_rcp)` expands to `struct ewma_<name>` with an `unsigned long internal` field, plus `ewma_<name>_init()`, `ewma_<name>_read()`, and `ewma_<name>_add()`. The precision controls fractional bits; `_weight_rcp` is the reciprocal of the new sample weight and must be a power of two.

## Control Flow
Init and read functions enforce compile-time constraints using `BUILD_BUG_ON()` and `BUILD_BUG_ON_NOT_POWER_OF_2()`. Add reads the current internal value with `READ_ONCE()`, computes `weight_rcp = ilog2(_weight_rcp)`, and writes either the first sample shifted by precision or the EWMA update `(((old << weight_rcp) - old) + (val << precision)) >> weight_rcp` via `WRITE_ONCE()`.

## State And Persistence
EWMA state is the caller-owned `internal` field. It persists as long as the containing object persists and is reset only by `ewma_*_init()`. The value is fixed-point internally and converted back to integer units by shifting right by `_precision` in `read()`.

## Dependencies And Integration Points
The macro depends on `linux/bug.h`, `linux/compiler.h`, and `linux/log2.h` for build-time validation, `READ_ONCE`/`WRITE_ONCE`, and `ilog2()`. It integrates with any subsystem that needs low-cost smoothing of counters or latency/throughput samples without floating point.

## Risks
The macro is not a full synchronization primitive; `READ_ONCE` and `WRITE_ONCE` avoid compiler tearing/reordering but do not serialize concurrent writers. Precision over 30 is rejected, but large sample values can still overflow `unsigned long` when shifted. Choosing an inappropriate weight can make the average too sluggish or too noisy.

## Test Signals
Compile-time tests should intentionally cover invalid precision and non-power-of-two weights in negative cases. Runtime unit tests can feed known sequences and verify first-sample behavior, smoothing math, truncation on read, and overflow-sensitive boundaries for 32-bit and 64-bit builds.
