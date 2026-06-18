# sources/distributed-fs/ipfs-kubo/core/coreapi/object.go

Purpose: implements DAG-PB object link add/remove/diff operations for CoreAPI with UnixFS safety checks.

Important APIs/types/functions: `ObjectAPI`, output shapes `Link` and `Node`, methods `AddLink`, `RmLink`, `Diff`, and `core`.

Control flow: add/remove resolve base and child paths, require base as `*dag.ProtoNode`, and unless validation is skipped, parse UnixFS data to permit only plain directories. HAMT shards and file-like UnixFS nodes are rejected because dag-pb link edits would corrupt UnixFS metadata. It then uses `dagutils.Editor` to insert/remove and finalize a new DAG node. `Diff` resolves before/after nodes, calls `dagutils.Diff`, and maps changes to CoreAPI paths.

State and persistence behavior: add/remove write new DAG nodes to the DAG service but do not mutate the original CID and do not pin by themselves. Diff is read-only.

Dependencies and integration points: relies on CoreAPI path resolution, boxo merkledag/dagutils/unixfs, and object command options for skip validation.

Risks: skip-validation can intentionally create invalid UnixFS DAGs. No pinning means new object CIDs may be garbage-collected unless pinned elsewhere. Validation only understands DAG-PB UnixFS data; non-UnixFS DAG-PB requires explicit override.

Test signals: likely covered by CoreAPI interface/object tests in the shared suite; no file-local tests.
