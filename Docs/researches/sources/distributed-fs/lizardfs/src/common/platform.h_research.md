<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/platform.h -->
# sources/distributed-fs/lizardfs/src/common/platform.h

## Purpose
Central compatibility header for generated config features, missing errno aliases, older standard-library functions, Judy width flags, and `thread_local` fallback. The source was read completely for this report.

## Important APIs, Types, And Functions
Defines FreeBSD `ENODATA`, fallback `std::to_string`, fallback `std::stoull`, `LIZARDFS_HAVE_64BIT_JUDY`, and fallback `thread_local __thread`.

## Control Flow
Preprocessor-only control flow selects definitions based on config/platform macros.

## State And Persistence Behavior
No runtime state or persistence.

## Dependencies And Integration Points
Included by almost every common source file; depends on generated `config.h`.

## Risks And Edge Cases
Global fallback definitions inside namespace `std` are compatibility hacks and can conflict with modern libraries if feature detection is wrong. `__thread` is not a full C++ `thread_local` replacement for non-trivial types.

## Test Signals
Build matrix coverage across Linux, FreeBSD, old GCC, Judy/non-Judy, and Windows-like targets is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/platform.h -->
