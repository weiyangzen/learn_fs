# sources/cloud-native/buildkit/cache/filelist.go

Purpose: derives and caches the sorted list of files represented by a cache ref's layer blob.

Important APIs/types/functions: constant `keyFileList` and method `(*immutableRef).FileList`.

Control flow: `FileList` uses `gFileList` flightcontrol keyed by ref ID to deduplicate concurrent calls. It first reads external metadata `filelist`; if present, JSON-unmarshals and returns it. If the ref has no blob, it returns nil. Otherwise it ensures lazy blob content is local, resolves the OCI descriptor, opens the blob from the content store, decompresses it, iterates tar headers, path-cleans names, sorts the result, JSON-marshals it, stores it in external metadata, and returns the list.

State and persistence behavior: persists a JSON array under external key `filelist` on the ref. It also may pull lazy blob content local via `ensureLocalContentBlob`, but does not create new blobs.

Dependencies and integration points: integrates containerd archive compression detection, content-store `ReaderAt`, tar reader, BuildKit sessions, and immutable ref descriptor handling. Consumers use the result to understand changed paths in a layer, including AUFS whiteout-format paths.

Risks: corrupt cached JSON fails the call. Tar path normalization with `path.Clean` may collapse unusual names. The list is empty for blobless refs, so callers must distinguish nil/empty from errors. Lazy content retrieval can introduce network/session failures.

Test signals: direct tests are not in this subset; behavior is covered by cache/export paths that rely on layer tar contents and metadata caching.
