
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/initialize.go

- Purpose: adds `mirror init` to initialize mirroring for the root directory.
- Important APIs: `newMirrorRootInodeCmd` and `runMirrorRootInode`.
- Control flow/state: the command is no-arg and gated by `--yes`; without confirmation it prints a dry-run warning and exits, otherwise calls `buddygroup.MirrorRootInode` and prints a restart/remount note.
- Dependencies/integration: integrates with `ctl/pkg/ctl/buddygroup` and `cmdfmt`; state change is persisted by the backend/management service, not by the CLI.
- Risks/tests: irreversible metadata state change; safety depends on user satisfying stopped-client and metadata mirror preconditions. No direct tests found.
