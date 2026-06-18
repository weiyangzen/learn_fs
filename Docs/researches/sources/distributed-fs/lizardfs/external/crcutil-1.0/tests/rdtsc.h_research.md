<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/rdtsc.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/rdtsc.h

## Purpose
Low-overhead cycle-counter abstraction used by crcutil performance tests.

## Important APIs, Types, and Functions
Defines `crcutil::Rdtsc` with static `uint64 Get()`. It uses `__rdtsc()` on MSVC x86/x64, inline `rdtsc` assembly on GCC AMD64 and i386, and returns `0` on unsupported platforms.

## Control Flow, State, and Persistence
The helper has no mutable state. On GCC i386 it captures low and high 32-bit halves separately and combines them; on GCC AMD64 it requests the low accumulator output into an `int64`, relying on the ABI/register behavior of `rdtsc`.

## Dependencies and Integration Points
Depends on crcutil `platform.h` for CPU and integer feature macros. `unittest.h` uses it to time initialization and CRC variants, reporting cycles per byte.

## Risks and Test Signals
Risks include non-serialized `rdtsc` measurements, CPU frequency migration effects, the AMD64 inline assembly not naming `edx` explicitly, unsupported platforms producing zero timings, and virtualized timers with unstable behavior. Test signals are monotonic-ish positive deltas on supported x86, graceful zero on unsupported builds, and performance tests not dividing by bogus zero-duration samples in practical runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/rdtsc.h -->
