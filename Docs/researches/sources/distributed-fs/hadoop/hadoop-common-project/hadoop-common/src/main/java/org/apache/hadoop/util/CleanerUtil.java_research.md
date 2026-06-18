# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CleanerUtil.java

Purpose: `CleanerUtil` provides an internal, version-adaptive hack for forcibly unmapping direct/mapped `ByteBuffer`s on Java 8 and Java 9+.

Important APIs and types: public constants `UNMAP_SUPPORTED` and `UNMAP_NOT_SUPPORTED_REASON`, `getCleaner()`, and functional interface `BufferCleaner.freeBuffer(ByteBuffer)`.

Control flow: static initialization runs privileged `unmapHackImpl`. It first tries Java 9+ `sun.misc.Unsafe.invokeCleaner(ByteBuffer)`, binding the unsafe singleton. If that fails, it tries Java 8 `DirectByteBuffer.cleaner().clean()` via `MethodHandle`s. The produced cleaner validates the buffer is direct and of the expected implementation class, invokes the unmapper under privilege, and wraps failures in `IOException`.

State and persistence behavior: stores one static cleaner or a static reason string. No persistence.

Dependencies and integration points: used by local filesystem/mmap code that needs deterministic unmap. Depends on private JDK APIs, `MethodHandles`, reflection, and security permissions.

Risks: highly JVM/security-manager dependent. Strong encapsulation can disable it. Passing non-direct or unsupported direct buffer subclasses throws `IllegalArgumentException`. Static initialization records support once for the process.

Test signals: cover supported and unsupported platforms, security-denied reason text, non-direct buffer rejection, wrong direct buffer implementation rejection, successful free path, and IOException wrapping from method-handle failure.
