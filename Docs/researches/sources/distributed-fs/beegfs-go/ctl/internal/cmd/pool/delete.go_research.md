
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/delete.go

- Purpose: implements `pool delete <pool>` with dry-run default.
- Important APIs: `deletePool_Config`, `newDeletePoolCmd`, and `runDeletePoolCmd`.
- Control flow/state: parses storage pool ID, calls `backend.Delete` with `Execute`, prints dry-run confirmation or deletion result, and warns about directory stripe patterns that still reference the pool ID.
- Dependencies/integration: uses `pm.DeletePoolRequest`, BeeGFS entity conversion, pool backend, and `cmdfmt`.
- Risks/tests: deleting referenced pools can make file creation fail; local command cannot scan references. Missing response identity is fatal only in dry run. No direct tests.
