## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/GetFileStatusOptions.java

### Purpose
`GetFileStatusOptions` carries optional behavior for file-status lookup, currently whether to include a real content hash.

### Important APIs, Types, And Functions
`defaults()` creates a new object with `includeRealContentHash=false`. `isIncludeRealContentHash` and `setIncludeRealContentHash` expose the flag.

### Control Flow
The flag is passed to `UnderFileSystem.getFileStatus(path, options)` so implementations can choose cheap placeholder hashes or compute/fetch stronger hashes.

### State And Persistence
Mutable in-memory option only.

### Dependencies And Integration Points
Used by file status and fingerprint-related flows. `UnderFileSystemWithLogging` currently drops this option when forwarding, which is an integration risk.

### Risks
No equals/hash/toString unlike other option classes. Callers going through the logging wrapper may not get requested real content hash behavior.

### Test Signals
No direct test for this class is in the requested subset.
