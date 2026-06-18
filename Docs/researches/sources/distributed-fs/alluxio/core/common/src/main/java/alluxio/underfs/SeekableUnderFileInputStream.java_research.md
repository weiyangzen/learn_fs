## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/SeekableUnderFileInputStream.java

### Purpose
This abstract class marks an under-file input stream as seekable. It wraps a regular `InputStream` with `FilterInputStream` while requiring subclasses to implement the `alluxio.Seekable` contract.

### Important APIs, Types, And Functions
The only constructor accepts the wrapped `InputStream` and passes it to `FilterInputStream`. The API surface is inherited: stream reads/delegation from `FilterInputStream` and seek/position methods from `Seekable`.

### Control Flow
There is no local read or seek implementation. Subclasses must reposition the wrapped stream when `seek(long)` is invoked.

### State And Persistence
State is the protected `FilterInputStream.in` delegate. No data is persisted.

### Dependencies And Integration Points
`UnderFileSystem.isSeekable()` documents that UFS implementations returning true should return streams extending this class from `open(String, OpenOptions)`.

### Risks
The class itself is simple; the risk is contractual. Returning true from `isSeekable` without returning this type, or implementing seek without synchronizing stream position, breaks positioned reads in upper layers.

### Test Signals
No direct test is in this subset. Coverage is expected in concrete UFS implementations with seekable stream support.
