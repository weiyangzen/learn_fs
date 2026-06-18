<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/libPVFS2JNI_common.h -->
# sources/distributed-fs/orangefs/src/client/jni/libPVFS2JNI_common.h

## Purpose

`libPVFS2JNI_common.h` centralizes common native JNI support macros for the OrangeFS Java user interface. It normalizes `_GNU_SOURCE`, disables `_FORTIFY_SOURCE` for this native layer, includes `errno`/`stdio`, defines a default Java `ArrayList` size, and provides optional debug/error-printing macros.

## Important APIs, Types, and Functions

Important macros are `JNI_INITIAL_ARRAY_LIST_SIZE`, `NULL_JOBJECT`, `JNI_PFI`, `JNI_PRINT`, `JNI_ERROR`, and `JNI_PERROR`. `ENABLE_JNI_ERROR` and `ENABLE_JNI_PERROR` are enabled by default; function-entry and generic print tracing are disabled unless the macros are uncommented.

## Control Flow

C JNI implementation files include this header and call the macros around native operations. `JNI_PERROR` checks `errno` and prints line/function information plus `perror` output when native calls fail.

## State, Persistence, and Concurrency

The header owns no persistent state. Its macros write to stdout/stderr and read global `errno`, so output from concurrent JNI calls may interleave.

## Dependencies and Integration Points

It is shared by `libPVFS2POSIXJNI.c` and `libPVFS2STDIOJNI.c`, and indirectly supports the Java classes in `org.orangefs.usrint`.

## Risks and Test Signals

Default stderr error printing can be noisy in Hadoop containers. Disabling `_FORTIFY_SOURCE` may hide buffer misuse diagnostics. Test by compiling the JNI library with expected flags and exercising failure paths to ensure Java callers receive null/error returns while native diagnostics remain interpretable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/libPVFS2JNI_common.h -->
