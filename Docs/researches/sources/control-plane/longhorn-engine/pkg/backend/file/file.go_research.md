<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backend/file/file.go -->
## sources/control-plane/longhorn-engine/pkg/backend/file/file.go

Purpose: local file-backed implementation of the Longhorn backend interface, mainly for simple/demo/test paths.

Important APIs/types/functions: `New` returns `Factory`. `Factory.Create` opens/creates an address as an `os.File` and wraps it. `Wrapper` embeds `*os.File` and implements backend methods: `UnmapAt`, `Snapshot`, revision counter setters/getters, rebuild reset, snapshot limit setters, monitor methods, `Size`, `Expand`, and metadata queries.

Control flow: reads/writes come from the embedded file. `Expand` validates the requested size, refuses shrink, truncates to the new size, and wraps rollback errors with Longhorn `types.Error` helpers if truncation or rollback fails.

State and persistence: persists data directly in the backing file. Most Longhorn-specific metadata methods return constants or no-ops: revision counter `1`, sector size `4096`, snapshot usage dummy values, state `open`, no monitor channel.

Dependencies and integration points: used by dynamic backend for `file://` addresses and by `launch-simple-file`. Depends on `os`, `logrus`, and `pkg/types`.

Risks: no real snapshotting, unmap, rebuild, or revision counter semantics; this backend should not be treated as equivalent to replica backends. Opening with `O_CREATE` can silently create new empty storage. No direct monitoring means controller cannot detect file-level failures through monitor channel.

Test signals: simple file backend smoke tests and expand behavior tests are most relevant.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backend/file/file.go -->
