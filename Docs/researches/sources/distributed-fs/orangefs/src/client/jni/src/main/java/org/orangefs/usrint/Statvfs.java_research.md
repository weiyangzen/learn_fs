# sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/Statvfs.java
## sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/Statvfs.java

**Purpose:** Java data carrier intended to mirror native `struct statvfs`.

**APIs and control flow:** Package-private fields include block size, fragment size, block and file counts, filesystem ID, flags, and max name length. The constructor is package-private and `toString()` reflectively dumps fields. In `PVFS2POSIXJNI`, statvfs methods are marked TODO, so this class is prepared but not actively surfaced by that class.

**State and dependencies:** Depends on future JNI native population. It has no getters and no current direct call path in the listed JNI API.

**Risks and tests:** Without native statvfs methods this can remain stale or untested. Like `Statfs`, field-width correctness depends on platform C types. Tests should be added with any JNI statvfs implementation and should include flag propagation and large filesystem counters.
