
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/root.go

- Purpose: root command assembly and global lifecycle for the BeeGFS CTL binary.
- Important APIs: `Execute`, `wrapAllCommands`, `attachCustomArgsErr`, `attachPersistentPreRunE`, `attachPersistentPostRunE`, `globalPersistentPreRunE`, `globalPersistentPostRunE`, `isCommandAuthorized`, help template utilities, and `pprofStarted`.
- Control flow/state: initializes global flags/config, registers all top-level commands, wraps argument and run hooks, installs custom help wrapping, creates an interrupt-cancelled context, executes Cobra, maps errors to exit codes, starts optional pprof once, enforces worker count and authorization, and runs quick health alerts after successful commands.
- Dependencies/integration: central integration point for every command package, Viper config, signal handling, logger, health quick checks, and OS effective UID.
- Risks/tests: global post-run health checks add remote calls to most successful commands; hook wrapping must avoid duplicate root execution. No direct tests in this subset.
