# sources/cloud-native/soci-snapshotter/metadata/reader.go

Purpose: bbolt-backed implementation of `metadata.Reader`. It parses ztoc TOC file metadata, builds a directory/node graph, persists attributes and tar-offset metadata, and serves lookup/open operations.

Important APIs/types/functions: `reader` holds db, fsID, rootID, section reader, ID counter/mutex, and init errgroup. Constructor `NewReader` applies options, records telemetry, initializes root and nodes, and returns a Reader. Build helpers include `init`, `initRootNode`, `initNodes`, `nextID`, `getIDByName`, `getOrCreateDir`, `setChild`, `cleanEntryPath`, `parentDir`, `partition`, and `attrFromZtocEntry`. Reader methods include `RootID`, `Clone`, `Close`, `GetAttr`, `GetChild`, `ForeachChild`, `OpenFile`, and test helper `NumOfNodes`.

Control flow: initialization creates a unique fsID bucket, root directory node, then partitions TOC entries into 5000-entry bbolt batches. For each TOC entry it normalizes paths, handles hardlinks by finding the destination node and incrementing link count, creates or updates node buckets for non-links, creates parent directories recursively, records parent-child relationships, and stores tar metadata for non-hardlinks. After node creation it writes sorted metadata buckets in batches. Read methods wait for initialization, open bbolt view/update transactions, find buckets by fsID and node ID, and reconstruct attributes or file metadata.

State and persistence: metadata lives under a unique bbolt filesystem bucket. `Close` deletes that fsID bucket from the shared DB. `Clone` shares db/fsID/rootID but swaps the section reader. Node IDs are process-generated uint32s guarded by a mutex. Hardlinks share node IDs and update link counts. Directory link counts are incremented for child directories.

Dependencies/integration points: consumes `ztoc.TOC` and `ztoc.FileMetadata`, stores bbolt buckets using helpers from `db.go`, and returns offset metadata needed to fetch file payloads. Uses `xid` for fsID uniqueness and `errgroup` for initialization wait plumbing, although current initialization is synchronous.

Risks: `NewReader` calls the telemetry hook immediately with `start`, so hook semantics are start-time based rather than after-duration unless the hook computes externally. `attr` is reused in the init loop; `attrFromZtocEntry` overwrites many fields but link count preservation for existing dirs depends on careful setup. `ForeachChild` returns map iteration order, not sorted order. Missing metadata in `OpenFile` yields zero offset/name rather than an explicit missing-metadata error if node exists. TODO notes no timeout for initialization wait.

Test signals: tests cover files, directories, hardlinks, symlinks, device nodes, FIFOs, xattrs, path cleanup, compression variants, telemetry hook invocation, and partition behavior.
