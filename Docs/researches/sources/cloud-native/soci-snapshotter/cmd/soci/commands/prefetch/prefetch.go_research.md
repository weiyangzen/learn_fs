## sources/cloud-native/soci-snapshotter/cmd/soci/commands/prefetch/prefetch.go

Purpose: command group definition for `soci prefetch`.

Important APIs/types/functions: `Command` and `JSONFlag`.

Control flow: registers `listCommand` and `infoCommand`; execution is delegated to those files.

State and persistence: none directly.

Dependencies and integration: urfave cli and sibling prefetch command implementations.

Risks and test signals: no direct tests; coverage depends on subcommand registration and behavior.
