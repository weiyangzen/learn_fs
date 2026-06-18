
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/create.go

- Purpose: implements `pool create <alias>` for storage pool creation and optional initial assignment.
- Important APIs: `createPool_Config`, `newCreatePoolCmd`, and `runCreatePoolCmd`.
- Control flow/state: parses alias, optional numeric ID, target/group slices, creates `pm.CreatePoolRequest` with storage node type, and warns when the pool starts empty.
- Dependencies/integration: uses BeeGFS alias/entity parsers, protobuf conversions, pool backend create, and `cmdfmt`.
- Risks/tests: empty pools are allowed but can break file creation for directories assigned to them until later assignment; backend handles ID uniqueness. No direct tests.
