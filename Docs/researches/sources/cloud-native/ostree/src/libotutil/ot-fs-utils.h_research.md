# sources/cloud-native/ostree/src/libotutil/ot-fs-utils.h

## Purpose
Declares fd-relative filesystem utility APIs and a cleanup helper for temporary unlink-at paths.

## Important APIs, Types, And Functions
Defines `OtCleanupUnlinkat`, `ot_cleanup_unlinkat_clear`, `ot_cleanup_unlinkat`, and cleanup macro support. Declares fd/path conversion, readlink-to-`GFileInfo`, open-read-stream, unlink-ignore-missing, open-ignore-missing, directory iterator allow-noent, anonymous tmpfile mapping, fd read/mmap, line parsing, and directory size APIs.

## Control Flow
The inline cleanup function calls `unlinkat` when a path is registered, then clears ownership. Other functions are declared only.

## State And Persistence Behavior
`OtCleanupUnlinkat` stores a directory fd and path to remove during cleanup. The declared APIs manipulate filesystem state but the header itself stores no global state.

## Dependencies And Integration Points
Depends on libglnx and `ot-unix-utils.h`, exposing Unix fd semantics to higher-level OSTree code.

## Risks
Cleanup ignores unlink errors, which is appropriate for best-effort temporary cleanup but can hide unexpected persistence. Callers must keep the directory fd valid for the cleanup lifetime.

## Test Signals
Compile tests for cleanup macros and behavioral tests in the implementation cover the header.
