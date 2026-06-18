# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/util.go

Purpose: provides a small atomic byte counter implementing `io.Writer`.

Important APIs and flow: `Counter.Write` atomically adds `len(p)` to an int64 and reports the full write length. `Counter.Size` atomically reads the accumulated count.

State and persistence: in-memory atomic counter only.

Dependencies and integration: used while packing upper and mount blobs to log generated blob sizes without wrapping the output stream in a separate counting writer.

Risks and test signals: simple and thread-safe for concurrent writes. It never returns partial writes or errors, which is appropriate for a side-channel counter.
