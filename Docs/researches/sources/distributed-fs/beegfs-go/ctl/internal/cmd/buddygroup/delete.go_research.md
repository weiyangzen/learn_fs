
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/delete.go

- Purpose: implements hidden `mirror delete <group>` for storage buddy group removal with a dry-run default.
- Important APIs: `deleteBuddyGroup_Config`, `newDeleteBuddyGroupCmd`, and `runDeleteBuddyGroupCmd`.
- Control flow/state: parses the storage group identifier with `NewEntityIdParser`, builds `pm.DeleteBuddyGroupRequest`, and passes `Execute` from `--yes`; dry run confirms deletability, while execute prints deletion success.
- Dependencies/integration: uses management backend `ctl/pkg/ctl/buddygroup.Delete`, `beegfs.EntityIdSetFromProto`, and `cmdfmt` user-facing output.
- Risks/tests: command warns about corruption conditions but cannot verify them locally; missing group info is fatal in dry run but only a warning after execution. No direct tests observed.
