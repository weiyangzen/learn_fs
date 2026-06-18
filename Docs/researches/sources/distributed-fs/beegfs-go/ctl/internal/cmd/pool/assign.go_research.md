
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/assign.go

- Purpose: implements `pool assign <pool>` for moving storage targets and buddy groups into a pool.
- Important APIs: `assignPool_Config`, `newAssignPoolCmd`, and `runAssignPoolCmd`.
- Control flow/state: requires at least targets or groups, parses each as storage entity IDs, converts to protobuf lists, calls `backend.Assign`, and prints assigned pool identity.
- Dependencies/integration: uses management protobuf `AssignPoolRequest`, BeeGFS entity conversion, and pool backend.
- Risks/tests: frontend does not check target/group current assignments or pool capacity; state mutation is persisted by management backend. No direct tests.
