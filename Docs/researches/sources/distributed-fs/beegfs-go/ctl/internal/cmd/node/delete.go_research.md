
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/delete.go

- Purpose: implements `node delete <node>` with dry-run default.
- Important APIs: `deleteNode_Config`, `newDeleteCmd`, and `runDeleteCmd`.
- Control flow/state: parses client/meta/storage node ID, calls `backend.Delete` with `Execute`, and prints dry-run or actual deletion result with metadata-specific warnings.
- Dependencies/integration: uses management protobuf `DeleteNodeRequest`, BeeGFS entity conversion, backend node delete, and `cmdfmt`.
- Risks/tests: destructive cluster membership mutation; local checks cannot prove node emptiness. Missing response identity is fatal in dry run but only warning after execute. No direct tests.
