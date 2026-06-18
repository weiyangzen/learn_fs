<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ashldi3.c -->
# sources/distributed-fs/ceph-client/lib/ashldi3.c

## Purpose
Provides the generic libgcc-style 64-bit arithmetic left shift helper `__ashldi3()` for architectures or compiler modes lacking a native helper.

## APIs, Types, and Functions
Exports `long long notrace __ashldi3(long long u, word_type b)`. It uses `DWunion` from `linux/libgcc.h` to access low and high 32-bit halves.

## Control Flow, State, and Persistence
If shift count is zero, it returns the input. Otherwise it computes `bm = 32 - b`. For shifts of 32 or more, the low half becomes zero and the high half is the old low half shifted by `b - 32`. For smaller shifts, carries from the low half fill the high half while the low half shifts left. There is no state; this is pure arithmetic.

## Dependencies and Integration
Depends on `linux/libgcc.h`, `linux/export.h`, and `notrace` because compiler-emitted helpers may be used from tracing-sensitive paths. Built when `CONFIG_GENERIC_LIB_ASHLDI3` is selected.

## Risks and Test Signals
Risks include undefined behavior for unsupported shift counts if callers/compiler ever pass values outside the expected 0-63 range, and ABI mismatches for `DWunion` layout. Test signals include compiler helper selftests on 32-bit targets, shifts by 0, 1, 31, 32, 33, 63, negative input bit patterns, and tracing builds verifying no instrumentation recursion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ashldi3.c -->
