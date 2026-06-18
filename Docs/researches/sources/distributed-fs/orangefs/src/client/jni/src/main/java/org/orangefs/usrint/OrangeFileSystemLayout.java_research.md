# sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/OrangeFileSystemLayout.java
## sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/OrangeFileSystemLayout.java

**Purpose:** Defines the Java enum used to pass OrangeFS file layout hints from the JNI-facing Java layer to native `openWithHints`.

**APIs and control flow:** Enum constants map directly to integer layout IDs: `PVFS_SYS_LAYOUT_NONE(1)`, `ROUND_ROBIN(2)`, `RANDOM(3)`, `LIST(4)`, and `LOCAL(5)`. The constructor stores the integer and `getLayout()` returns it. There is no parsing beyond normal Java `Enum.valueOf`.

**State and dependencies:** The enum is immutable and has no external dependencies. Its integer values must stay synchronized with the C `PVFS_sys_layout`/`PVFS_SYS_LAYOUT_*` constants used by the JNI native implementation.

**Risks and tests:** The main risk is ABI drift between Java constants and native OrangeFS layout IDs; changing either side silently changes data-placement behavior. Current tests check `getLayout()` and `valueOf()`, but do not exercise native open behavior. Integration tests should create files with each layout through `OrangeFileSystemOutputStream` and verify server/datafile placement or native acceptance.
