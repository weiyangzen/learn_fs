<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/ioutils/countwriter.go -->
# sources/cloud-native/stargz-snapshotter/util/ioutils/countwriter.go

## Purpose
Provides a simple writer that counts bytes written without storing them.

## Important APIs, Types, And Functions
- `CountWriter` holds an `int64` byte count.
- `Write(p []byte)` increments the count by `len(p)` and reports full success.
- `Size()` returns the accumulated count.

## Control Flow
Each write converts input length to int64, adds it to the counter, and returns `len(p), nil`.

## State And Persistence
State is the in-memory byte count. It is not synchronized for concurrent writes.

## Dependencies And Integration Points
Useful anywhere an `io.Writer` is needed solely to measure serialized size or stream length.

## Risks And Edge Cases
Not thread-safe. Count can overflow int64 on extreme input totals. It never returns write errors, so it should not be used to simulate real sink failures.

## Test Signals
Expected tests write several byte slices and assert returned counts and final `Size`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/ioutils/countwriter.go -->
