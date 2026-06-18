<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/main.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/main.go

- Purpose: Main CLI entry point and command registry dispatcher for the `containers-storage` diagnostic/admin tool.
- Important types/functions: `command`, global `commands`, `jsonOutput`, `force`, `main`, and `outputJSON`.
- Control flow: Initialize reexec, parse global flags into `types.StoreOptions`, load default options when none are supplied, resolve subcommand, parse command-specific flags, optionally reexec in a user namespace, set log level, open store with `storage.GetStore`, run command action, and exit with returned status.
- State and persistence: Store initialization may create/use lock files and storage roots. `store.Free()` is called before action, which is unusual but likely releases process-global store reference while leaving the handle usable.
- Dependencies and integration: Uses `mflag`, `unshare`, `reexec`, storage options, and command files that append in `init`.
- Risks: Commands rely on package init ordering only for registry population; `store.Free()` placement needs care if store lifetime expectations change.
- Test signals: CLI smoke tests for parsing, namespace behavior, JSON output, and command dispatch.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/main.go -->
