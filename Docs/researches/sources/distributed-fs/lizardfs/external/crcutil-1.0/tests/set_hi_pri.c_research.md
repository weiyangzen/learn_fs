<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/set_hi_pri.c -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/set_hi_pri.c

## Purpose
Optional Windows-only helper that raises the crcutil unittest process and main thread priority to reduce timing noise in performance measurements.

## Important APIs, Types, and Functions
Exports C-linkage `void SetHiPri(void)`. On `_WIN32`, it calls `SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_TIME_CRITICAL)` and `SetPriorityClass(GetCurrentProcess(), REALTIME_PRIORITY_CLASS)`. On non-Windows platforms the function is a no-op.

## Control Flow, State, and Persistence
There is no persistent application state besides process scheduler priority on Windows. The source includes MSVC warning suppressions around `windows.h` and uses an `#if 1` block selecting the most aggressive realtime priority path over a milder high-priority alternative.

## Dependencies and Integration Points
Depends on Win32 APIs when `_WIN32` is defined. `unittest.cc` declares `extern "C" void SetHiPri();` and calls it before constructing CRC verifiers.

## Risks and Test Signals
Risks are explicitly high on Windows: realtime/time-critical priority can make a machine unresponsive if tests hang. Return values are ignored, so permission failures are silent. Test signals include linking the C function into the C++ unittest binary, no-op behavior on Unix builds, and observable priority changes or harmless failure on Windows without administrator rights.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/set_hi_pri.c -->
