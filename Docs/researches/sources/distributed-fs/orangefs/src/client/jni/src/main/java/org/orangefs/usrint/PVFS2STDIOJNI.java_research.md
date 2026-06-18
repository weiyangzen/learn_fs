# sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/PVFS2STDIOJNI.java
## sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/PVFS2STDIOJNI.java

**Purpose:** Java JNI declaration class for OrangeFS/PVFS stdio and directory-style operations, exposing `FILE*`/`DIR*` handles as Java `long` values.

**APIs and control flow:** Static initialization mirrors `PVFS2POSIXJNI` by loading `libpvfs2.so`, `liborangefs.so`, and `libofs.so` from `JNI_LIBRARY_PATH` and exiting on failure. The constructor fills `PVFS2STDIOJNIFlags`. Native methods cover file stream locking, read/write/get/put calls, seek/tell/flush/close, directory open/read/seek/tell/close, temporary files, user/group lookup, recursive delete, and utility directory listing. `toString()` reflectively dumps instance fields.

**State and dependencies:** State is the native-filled flags object. It depends on native C stdio wrappers, `ArrayList<String>` for directory entry listing, and stable pointer-size mapping through Java `long`.

**Risks and tests:** Raw native pointers represented as `long` lack lifetime safety and can be reused after close. The class exits the JVM on library-load failure. String-returning functions such as `fgets` depend on JNI memory conversion. Tests should exercise open/read/write/seek/close, directory traversal, flag population, pointer misuse after close, and both locked and unlocked variants.
