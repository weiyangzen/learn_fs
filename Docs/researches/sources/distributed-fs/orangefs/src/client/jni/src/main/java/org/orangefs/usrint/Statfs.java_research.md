# sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/Statfs.java
## sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/Statfs.java

**Purpose:** Java data carrier for native `struct statfs` returned by JNI filesystem-stat calls.

**APIs and control flow:** Package-private fields represent filesystem type, block size, block counts, file counts, fsid, name length, and fragment size. The constructor is package-private for JNI use. `getCapacity()`, `getUsed()`, and `getRemaining()` expose `f_bsize`, `f_bfree`, and `f_bavail` respectively, and `toString()` reflectively dumps fields.

**State and dependencies:** Populated by `PVFS2POSIXJNI.statfs` and `fstatfs`. It assumes native code can access package-private fields via JNI.

**Risks and tests:** The getter names are suspicious: capacity usually implies `f_blocks * f_bsize`, and used usually implies `(f_blocks - f_bfree) * f_bsize`, not raw block size/free blocks. Field visibility may limit outside-package inspection. Test signals should validate getter semantics against expected filesystem stats and compare all raw fields to native `statfs`.
