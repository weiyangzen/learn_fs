# sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/PVFS2POSIXJNIFlags.java
## sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/PVFS2POSIXJNIFlags.java

**Purpose:** JNI-filled holder for POSIX open flags, mode bits, seek constants, `*at` flags, statfs flags, and access-mode constants.

**APIs and control flow:** Fields are public `long` values populated by native `PVFS2POSIXJNI.fillPVFS2POSIXJNIFlags()`. Constructor is private to discourage Java-side creation. `toString()` reflectively prints all declared fields.

**State and dependencies:** State is entirely native-populated and platform-dependent. Consumers include input/output streams and tests that need constants such as `O_RDONLY`, `O_CREAT`, `S_IRWXU`, and `SEEK_SET`.

**Risks and tests:** If native population misses a field, Java code receives zero and can open files with wrong flags or modes. Reflection output includes every declared field, so adding fields changes diagnostics. Because constructor is private, tests must obtain instances through the JNI class or reflection. Test signals should compare every field against native constants on target platforms and verify `toString()` does not throw under security/access constraints.
