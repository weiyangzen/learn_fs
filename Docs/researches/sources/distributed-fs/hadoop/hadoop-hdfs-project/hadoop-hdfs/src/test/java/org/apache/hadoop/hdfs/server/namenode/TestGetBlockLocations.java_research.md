# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGetBlockLocations.java

**Purpose:** Unit-level coverage for `FSNamesystem.getBlockLocations()` when paths are addressed through `/.reserved/.inodes/<id>`, especially atime edit logging under delete and rename races.

**Important APIs and flow:** `setupFileSystem()` constructs an `FSNamesystem` with mocked `FSImage` and `FSEditLog`, creates an `INodeFile` with a known inode ID, and inserts it into `FSDirectory` under `/foo`. Tests call `fsn.getBlockLocations("dummy", RESERVED_PATH, 0, 1024)` and use Mockito verification on `editlog.logTimes()`.

**Control flow:** `testResolveReservedPath()` verifies the reserved inode path is resolved to `/foo` before logging access times. `testGetBlockLocationsRacingWithDelete()` spies `FSNamesystem.checkOperation(WRITE)` to delete the file just before the real operation proceeds, then asserts atime is not logged for a deleted inode. `testGetBlockLocationsRacingWithRename()` similarly renames `/foo` to `/bar` and asserts atime logging uses `/bar`.

**State and persistence behavior:** The mocked edit log is the persistence signal: `logTimes(path, mtime, atime)` is expected only when the inode still exists and with the post-resolution path after rename. The in-memory namespace is mutated under FS or global write locks to model racing metadata changes.

**Dependencies and integration points:** Integrates `FSNamesystem`, `FSDirectory`, `FSDirDeleteOp`, `FSDirRenameOp`, `INodesInPath`, `INodeFile`, edit-log atime logging, and reserved inode path resolution. Mockito spies are used to inject races at operation-category checks.

**Risks and test signals:** The race is synthetic and depends on the current placement of `checkOperation(WRITE)` inside `getBlockLocations()`. A pass signals reserved inode paths resolve before atime persistence, deletes suppress stale atime edits, and renames persist access-time updates under the current canonical path.
