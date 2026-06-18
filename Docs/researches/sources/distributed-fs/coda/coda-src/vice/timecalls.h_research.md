# sources/distributed-fs/coda/coda-src/vice/timecalls.h

## Purpose

`sources/distributed-fs/coda/coda-src/vice/timecalls.h` defines optional fine-grained timing macros for Coda server operations, including support for a platform-specific NSC hardware/software counter accessed through an ioctl-like device and fallback wall-clock timing.

## Important APIs, Types, and Functions

The header declares `clockFD` and histogram objects for create/remove/link/rename/mkdir/rmdir/symlink, log spooling, and `PutObjects` phases. It defines `NSC_SHOW_COUNTER_INFO`, `NSC_GET_COUNTER`, `START_NSC_TIMING(id)`, and `END_NSC_TIMING(id)`.

## Control Flow

When `_TIMECALLS_` is defined, `START_NSC_TIMING` starts normal `START_TIMING`, captures either `NSC_GET_COUNTER` or `gettimeofday`, and `END_NSC_TIMING` computes elapsed time, handles counter wrap, and updates `id_hg`. Without `_TIMECALLS_`, the macros collapse to the normal `START_TIMING`/`END_TIMING` instrumentation.

## State and Persistence Behavior

The file owns no persistent data. It mutates histogram accumulators and reads `clockFD`. Timing state is macro-local and transient; histogram state lives in the instrumentation module that defines the declared `hgram` globals.

## Dependencies and Integration Points

It depends on `histo.h`-style `struct hgram` declarations, `UpdateHisto`, `START_TIMING`, `END_TIMING`, system `ioctl`, `gettimeofday`, and Mach headers. `srvproc.cc` uses these macros around `PutObjects` phases when timing builds are enabled.

## Risks and Edge Cases

The macros declare local variables by token-pasting the timing id, so they must be used in scopes where repeated ids do not collide. The counter wrap constant and division by 25 are platform-specific. The header uses old-style preprocessor comments on `#else __STDC__`/`#endif __cplusplus`, which may warn on modern compilers.

## Test Signals

Compile both with and without `_TIMECALLS_`; run a timing-enabled server and verify histogram updates for `PutObjects` and mutation operations; test fallback behavior when `clockFD <= 0`; and build on modern compilers with warnings enabled to catch stale preprocessor syntax issues.
