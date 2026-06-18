# sources/distributed-fs/juicefs/pkg/object/mem.go


Purpose: implements an in-memory object storage registered as `mem`, primarily for tests and local transient use.

Important APIs and flow: `memStore` protects a map of key to `mobj` with a mutex. `Head`, `Get`, `Put`, `Copy`, `Delete`, and `List` implement the common object contract. Empty keys are rejected. `Get` slices byte data by offset/limit. `Put` reads the entire input and stores mtime as `time.Now()`. `List` scans all keys, handles delimiter common prefixes, sorts by key, applies limit, and calls `generateListResult`.

State and persistence: all state is process-local memory in `objects`; it is lost on process exit. `mobj` can hold mode, owner, and group fields, but `Put` currently stores only data and mtime.

Dependencies and integration: embeds `DefaultObjectStorage` and returns `file` metadata objects so tests can use common file/object assertions. Used heavily by encryption and object-storage tests.

Risks: no persistence, no efficient large-object handling, and no context cancellation. The delimiter code derives common-prefix metadata from the first matching object, which may carry mostly empty owner/mode values. Copy does not close the reader returned by `Get`.

Test signals: `TestMem`, encryption tests, chunked encryption tests, sharding tests, and many helper paths rely on this backend.
