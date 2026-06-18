<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/Orange.java -->
# sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/Orange.java

## Purpose

`Orange` is the Java singleton facade for the OrangeFS direct-client JNI layer. It centralizes construction of `PVFS2POSIXJNI` and `PVFS2STDIOJNI` wrappers so higher-level code can access POSIX-style and stdio-style native operations through one object.

## Important APIs, Types, and Functions

The public API is `Orange.getInstance()`, returning the holder-based singleton. Public fields `posix` and `stdio` expose initialized `PVFS2POSIXJNI` and `PVFS2STDIOJNI` instances. The constructor is private.

## Control Flow

The nested `OrangeHolder` lazily initializes the singleton when `getInstance` is first called. The constructor creates both JNI wrapper objects, which are then reused by Hadoop adapters and Java stream classes.

## State, Persistence, and Concurrency

The singleton stores two mutable public wrapper references. It does not persist filesystem state itself; all persistence is through native calls. Holder-based initialization is thread-safe in Java, but the public fields can be reassigned by any code with access.

## Dependencies and Integration Points

It depends on the generated/manual JNI Java classes in `org.orangefs.usrint` and their native library bindings. `OrangeFileSystem` and `OrangeFileSystemUnderlying` call it during construction.

## Risks and Test Signals

Public mutable fields weaken singleton invariants. Tests should verify native library loading, flag initialization, and basic `posix.stat`/`stdio.getEntriesInDir` calls through `Orange.getInstance()` from multiple callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/Orange.java -->
