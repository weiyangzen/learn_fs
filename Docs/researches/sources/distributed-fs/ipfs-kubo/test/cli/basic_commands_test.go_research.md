# sources/distributed-fs/ipfs-kubo/test/cli/basic_commands_test.go

Purpose: broad CLI sanity suite covering version output, command discovery, help consistency, documentation width, bad flag handling, and command flag listing.

Important functions: `parseVersionOutput`, `TestCurDirIsWritable`, `TestIPFSVersionCommandMatchesFlag`, `TestIPFSVersionAll`, `TestIPFSVersionDeps`, `TestIPFSCommands`, `TestAllSubcommandsAcceptHelp`, `TestAllRootCommandsAreMentionedInHelpText`, `TestCommandDocsWidth`, `TestAllCommandsFailWhenPassedBadFlag`, and `TestCommandsFlags`. It uses `IPFSCommands()` to enumerate commands and runs help/bad-flag checks against each.

Control flow is mostly parallel subtests. Version parsing uses a regexp and semver. Dependency output is split on replacements and validated with `golang.org/x/mod/module.Check`, skipping local replace paths. Help text root commands are compared to command discovery with a small exclusion map; width checks enforce 80 columns unless allowlisted. State is transient command output only. Dependencies are harness command execution, command registry output, semver parsing, module path validation, and testutils helpers. Risks include allowlist churn when docs change, command output formatting changes, and broad loops increasing test time. Test signal is high-level CLI contract coverage.
