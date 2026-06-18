# sources/cloud-native/buildkit/client/ociindex/ociindex.go

## Purpose
This package manages the `index.json` and `oci-layout` files for a local OCI content store used by client-side cache and image exports. It provides a small, locked API for reading an OCI image index, adding descriptors with optional image names/tags, and resolving descriptors by tag or single-manifest layout.

## Important APIs, Types, and Functions
- `StoreIndex` stores paths to `index.json`, `index.json.lock`, and `oci-layout`.
- `NameOrTag`, `Name`, and `Tag` describe how a descriptor should be annotated when inserted.
- `NewStoreIndex(storePath)` binds index management to a local content-store directory.
- `Read()` takes a shared lock, reads `index.json`, and unmarshals an `ocispecs.Index`.
- `Put(desc, names...)` takes an exclusive lock, writes `oci-layout`, reads or creates `index.json`, applies OCI defaults, inserts one descriptor per supplied name/tag, writes the JSON back at offset zero, and truncates stale bytes.
- `Get(tag)` resolves first by `io.containerd.image.name`, then by OCI `org.opencontainers.image.ref.name`.
- `GetSingle()` returns the only manifest when the index contains exactly one descriptor.
- `insertDesc` clones descriptor annotations, adds name/tag annotations, removes replaced descriptors, and appends the new descriptor.

## Control Flow
`Put` is the main mutating path. It acquires a flock, ensures an OCI layout file exists, opens the index with create permissions, decodes existing JSON if present, fills schema and media type defaults, converts missing names into a single nil insertion, and appends/replaces descriptors. `Read`, `Get`, and `GetSingle` are read-only paths, with `Get` performing two lookup passes for containerd full-image-name compatibility and OCI tag compatibility.

## State and Persistence Behavior
State is persisted entirely as JSON files in the store path. The lock file is removed after lock release. `Put` overwrites `index.json` in place and truncates it, so callers rely on flock protection for concurrent writers. The descriptor passed by the caller is copied before annotation changes, avoiding mutation of caller-owned state.

## Dependencies and Integration Points
The package depends on OCI image-spec types, containerd reference parsing, `gofrs/flock`, and POSIX-style lock errors. It is used by `client/solve.go` to update local cache stores and output stores after successful solves and by cache import logic to resolve tags into digests.

## Risks and Edge Cases
The read path tolerates `EPERM` and `EROFS` lock errors by continuing without a lock, which is useful on read-only/limited filesystems but weakens concurrency guarantees. `Put` does not use a temp-file rename, so a process crash during write could leave partial JSON. Replacement only removes descriptors whose OCI ref and containerd image-name annotations both match the new insertion semantics, so changing naming rules can create duplicates.

## Test Signals
`ociindex_test.go` covers missing indexes, reading, single descriptor writes, tag lookups, default fields, multiple names per descriptor, and replacement by image name. `solve.go` and `solve_resetcache_test.go` provide integration pressure by relying on the index for cache imports, exports, and reset reachability.
