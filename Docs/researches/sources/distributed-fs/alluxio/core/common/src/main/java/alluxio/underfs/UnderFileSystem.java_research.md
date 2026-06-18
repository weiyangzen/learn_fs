## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystem.java

### Purpose
`UnderFileSystem` is the central public contract for storage systems beneath Alluxio. It defines file, directory, metadata, ACL, fingerprint, active sync, listing, and lifecycle operations and distinguishes ordinary operations from eventual-consistency-aware variants.

### Important APIs, Types, And Functions
The nested `Factory` creates wrapped UFS instances by consulting `UnderFileSystemFactoryRegistry`, trying eligible factories with recorder logging and context classloader switching, wrapping successful clients in `UnderFileSystemWithLogging`, and exposing `createForRoot` for root mount configuration. `SpaceType` enumerates total/free/used space.

The interface includes lifecycle (`cleanup`, `close`, connect from master/worker), create/delete/rename/open/mkdir APIs, status and listing APIs, ACL/owner/mode mutation, file locations, fingerprints, operation mode, physical stores, object/seekable flags, URI resolution, flush support, active sync polling, sync point management, and inherited async listing/rate limiter methods from `UfsClient`.

### Control Flow
The factory path is important: find all factories, iterate in order, switch the current thread context classloader to the factory classloader, call `factory.create`, wrap in logging, return first success, and collate suppressed errors if all candidates fail. Root creation pulls root UFS URI, read-only flag, and root mount options from configuration.

### State And Persistence
The interface holds no state. Implementations persist data in their backing stores and may hold connections, credentials, threads, caches, and mount-specific configuration.

### Dependencies And Integration Points
This is used by Alluxio master, worker, journal, metadata sync, and mount machinery. It depends on Alluxio configuration, recorder, ACL types, `UfsStatus` types, option classes, `SyncInfo`, and `AlluxioURI`.

### Risks
The API is broad and includes legacy/deprecated methods. Implementations must honor eventual-consistency variants, atomic create semantics, full-path listing expectations for async sync, and seekable-stream contracts. Factory selection can be affected by service loader ordering, shading, and version matching.

### Test Signals
`UnderFileSystemTest` verifies that core-only factory discovery does not claim local, HDFS, OSS, S3, S3A, or Gluster paths without external modules. Many method contracts are tested through concrete UFS modules outside this subset.
