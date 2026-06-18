## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/FileLocationOptions.java

### Purpose
`FileLocationOptions` carries an offset for querying physical file locations from a UFS.

### Important APIs, Types, And Functions
`defaults()` initializes offset zero. `getOffset` and `setOffset` expose the offset. Equality, hash code, and `toString` include it.

### Control Flow
The option is passed to `UnderFileSystem.getFileLocations(path, options)`. Object stores return null by default because locations are unsupported.

### State And Persistence
Mutable in-memory option only.

### Dependencies And Integration Points
Used by storage-aware scheduling/location queries in UFS implementations that can map file offsets to hosts.

### Risks
There is no validation for negative offsets in this object; implementations must validate if needed.

### Test Signals
`FileLocationOptionsTest` verifies default offset and setter behavior across several offsets, plus equality.
