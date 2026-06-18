# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/NativeLibraryChecker.java

## Purpose

`NativeLibraryChecker` is a command-line diagnostic that prints availability of Hadoop native libraries and exits nonzero when required native support is missing.

## Important APIs, Types, And Functions

The only public entry point is `main(String[] args)`. It supports `-h` for usage and `-a` to require additional native libraries. It checks Hadoop native code, zlib, bzip2, OpenSSL, ISA-L, PMDK, and Windows `winutils.exe`.

## Control Flow, State, And Persistence

Argument validation prints usage and terminates via `ExitUtil`. The checker creates a `Configuration`, queries each subsystem's factory/loading state, prints a table, and calls `ExitUtil.terminate(1)` if required checks fail. No persistent state is changed.

## Dependencies And Integration Points

It depends on `NativeCodeLoader`, `ZlibFactory`, `Bzip2Factory`, `OpensslCipher`, `ErasureCodeNative`, `NativeIO`, `Shell`, and `ExitUtil`. It is used by administrators, build validation, and diagnostics.

## Risks And Test Signals

The `-a` failure condition requires zlib, bzip2, and ISA-L but prints OpenSSL/PMDK details without requiring them. Windows output includes `winutils` twice. Tests should disable exits, exercise `-h`, invalid args, default vs `-a`, Windows/non-Windows paths, and loaded/failure detail strings.
