<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/exception.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/exception.h

## Purpose
`exception.h` declares Hadoop native exception helpers and the errno string helper. It is the shared contract for C/JNI files that want to create Java exceptions without duplicating JNI lookup and formatting logic.

## Important APIs, Types, and Functions
The header declares `newExceptionV()`, `newException()`, `newRuntimeException()`, `newIOException()`, and `terror()`. It also defines `TYPE_CHECKED_PRINTF_FORMAT`, which expands to GCC's `format(printf, ...)` attribute on non-Windows builds and to a stub on Windows.

## Control Flow
There is no executable control flow in the header. Compile-time flow is platform-conditional: non-Windows callers get format-string checking for the variadic helpers; Windows callers compile without the GCC attribute.

## State and Persistence
The header owns no state. It only exposes function prototypes and a temporary annotation macro that is undefined at the end of the file.

## Dependencies and Integration Points
It includes JNI types, `stdarg.h`, and Hadoop native platform definitions. The declarations are used by socket, NativeIO, group mapping, erasure-code, and other JNI wrappers that throw Java exceptions.

## Risks and Edge Cases
The comments promise no pending exceptions on return, which places a strong behavioral contract on `exception.c`. Callers must still explicitly throw the returned `jthrowable`; forgetting that step silently drops errors.

## Test Signals
Builds should show printf-format warnings for mismatched format arguments on Unix-like toolchains. Runtime tests should verify helper-created Java exception classes and messages from representative JNI wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/exception.h -->
