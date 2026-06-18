<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/NativeIOException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/NativeIOException.java

## Purpose
`NativeIOException` wraps errors returned by Hadoop native I/O calls. On POSIX it carries an `Errno`; on Windows it carries a raw system error code.

## Important APIs and Types
Constructors accept `(String msg, Errno errno)` or `(String msg, int errorCode)`. Accessors `getErrno` and `getErrorCode` expose the platform-specific payload. `toString` selects error-code formatting on Windows and errno formatting elsewhere.

## Control Flow
The class has no complex flow. Callers choose the constructor that matches platform/native failure information, and downstream code inspects either `Errno` or integer error code.

## State and Persistence
Instances are serializable as `IOException` subclasses, with `serialVersionUID = 1L`. The POSIX constructor initializes Windows error code to success `0`; the Windows constructor initializes errno to `UNKNOWN`.

## Dependencies and Integration Points
It is used throughout `NativeIO` to translate JNI failures into Java exceptions and by callers that branch on `EEXIST`, Windows `ERROR_FILE_EXISTS`, invalid-handle codes, and similar conditions. It depends on `Shell.WINDOWS` for formatting.

## Risks and Edge Cases
`getErrorCode` returns `long` but stores an `int`; unsigned 32-bit Windows codes above `Integer.MAX_VALUE` are represented as signed values internally. Formatting is based on the current runtime OS rather than which constructor was used, so cross-platform serialized inspection may be confusing.

## Test Signals
Tests should verify POSIX and Windows constructor payloads, string formatting under platform conditions, and caller translations for representative errno/error-code values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/NativeIOException.java -->
