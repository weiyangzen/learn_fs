# sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/PVFS2STDIOJNIFlags.java
## sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/PVFS2STDIOJNIFlags.java

**Purpose:** JNI-filled holder for stdio seek constants, directory entry `d_type` constants, and setvbuf mode constants.

**APIs and control flow:** Public `long` fields include `SEEK_SET/CUR/END`, `DT_*`, and `_IONBF/_IOLBF/_IOFBF`. The public constructor permits Java creation, but useful values come from `PVFS2STDIOJNI.fillPVFS2STDIOJNIFlags()`. `toString()` reflectively dumps fields.

**State and dependencies:** Platform-dependent numeric constants are copied from native C. Consumers are Java JNI tests and any stdio wrappers needing seek or directory type constants.

**Risks and tests:** Public construction can produce an all-zero flags object if callers bypass the JNI factory. Platform differences in `DT_*` and buffering constants must be captured by native fill logic. Test signals should verify all fields are nonzero where expected on the target platform, compare with native constants, and cover `toString()` reflection.
