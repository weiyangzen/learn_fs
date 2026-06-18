# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/FileSystemMasterView.java

Purpose: synchronized read-only facade over `FileSystemMaster`, used by other master components that need file metadata and worker information without exposing mutation APIs.

Important APIs and types: constructor requires a non-null `FileSystemMaster`. Synchronized methods include `getFileInfo`, `getFileId`, `getFileBlockInfoList`, `getPath`, and `getWorkerInfoList`.

Control flow: each method simply delegates to the underlying master while serializing access on the view object. Exceptions from the underlying master are propagated.

State and persistence behavior: no state beyond the delegate reference. Read methods may trigger metadata load depending on underlying master behavior, but this facade does not persist data itself.

Dependencies and integration points: depends on `FileSystemMaster`, `AlluxioURI`, wire types, and Alluxio exception types. It integrates with block master or other components needing read-only file-system master access.

Risks: synchronization here serializes only calls through this view, not all access to the underlying master. Long-running delegated calls can block other view users.

Test signals: tests should cover delegation, null delegate rejection, exception propagation, and synchronization if concurrent use matters.
