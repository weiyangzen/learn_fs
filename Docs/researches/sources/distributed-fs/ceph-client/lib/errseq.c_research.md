# sources/distributed-fs/ceph-client/lib/errseq.c

## Purpose
Implements `errseq_t`, a compact lockless sequence/error word for recording errors in one place and letting many observers detect whether a new error occurred since their sample. It is commonly used for writeback and filesystem error reporting.

## Important APIs, Types, and Functions
Exported APIs are `errseq_set()`, `errseq_sample()`, `errseq_check()`, and `errseq_check_and_advance()`. Internal bit layout macros are `ERRSEQ_SHIFT`, `ERRSEQ_SEEN`, `ERRNO_MASK`, and `ERRSEQ_CTR_INC`. The low bits store a positive errno magnitude, one bit marks whether the value has been seen, and upper bits act as a counter.

## Control Flow
`errseq_set()` validates a nonzero negative errno, clears old errno and seen bits, stores the new errno magnitude, and increments the counter only if a reader had marked the old value seen. It uses `cmpxchg()` loops and treats racing writes to the same value as success. `errseq_sample()` returns zero when an error is still unseen so a new observer will still report it later. `errseq_check()` compares a stored sample with the current value and returns the current error without advancing. `errseq_check_and_advance()` sets the seen bit, updates the caller's sample, and returns the recorded error.

## State and Persistence
All persistent state is the caller-owned `errseq_t` word. There is no allocation or global state. Updates are atomic and usable from any context, but concurrent access to a caller's `since` sample pointer is not serialized by this file.

## Dependencies and Integration Points
Depends on kernel atomics, `MAX_ERRNO`, `linux/errseq.h`, and `linux/log2.h`. Filesystems and writeback code integrate by embedding `errseq_t` fields in shared objects and storing per-file/per-observer samples.

## Risks
The counter has limited width, so very frequent errors can theoretically collide with old samples. `errseq_check()` reports the latest stored errno, not necessarily the first error since the sample. Callers must provide locking if multiple threads advance the same sample. Passing zero, positive, or out-of-range errors to `errseq_set()` only warns and leaves state unchanged.

## Test Signals
Tests should cover initial zero state, unseen error sampling, seen-bit behavior, repeated same-error sets before/after sampling, racing set/check patterns, invalid error inputs, and counter wrap/collision scenarios. Filesystem tests should verify that errors are reported once per observer after advance.
