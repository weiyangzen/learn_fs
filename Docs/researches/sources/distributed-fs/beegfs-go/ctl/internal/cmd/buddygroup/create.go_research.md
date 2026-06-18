
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/create.go

- Purpose: defines `mirror create` and `mirror autocreate` for manual and automatic buddy group creation.
- Important APIs: `createBuddyGroup_Config`, `newCreateBuddyGroupCmd`, `newCreateBuddyGroupsAutomaticCmd`, `runCreateBuddyGroupCmd`, and `runCreateBuddyGroupsAutomaticCmd`.
- Control flow/state: Cobra parses alias, node type, numeric ID, primary, and secondary targets into BeeGFS entity types, then sends `pm.CreateBuddyGroupRequest` through `ctl/pkg/ctl/buddygroup.Create`; autocreate delegates to `backend.AutoCreate` and prints each created group plus warnings.
- Dependencies/integration: relies on `beegfs` parsers/proto conversion, `cmdfmt`, management protobufs, and `util.NewCtlError` for partial success.
- Risks/tests: no local tests in this file; risk is mostly destructive cluster state mutation and warning handling, especially continuing after partial automatic creation.
