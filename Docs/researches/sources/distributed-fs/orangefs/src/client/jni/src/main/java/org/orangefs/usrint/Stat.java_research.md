# sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/Stat.java
## sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/Stat.java

**Purpose:** Java data carrier for native `struct stat` results returned by POSIX JNI methods.

**APIs and control flow:** Public fields mirror common stat members: device, inode, mode, link count, uid/gid, rdev, size, block size/count, and atime/mtime/ctime. The package-private constructor is intended for JNI instantiation/population. `toString()` reflectively prints all fields.

**State and dependencies:** State is populated by native code in `PVFS2POSIXJNI.stat`, `fstat`, `lstat`, and `fstatat`. Field widths are chosen as Java `long` or `int` and must match JNI conversion decisions on supported platforms.

**Risks and tests:** Native structure width differences can truncate mode, link count, block size, or IDs if mappings are wrong. Public mutable fields make values easy to corrupt after return. Test signals should compare Java fields to native stat output for regular files, directories, symlinks, large files, and unusual ownership/mode bits.
