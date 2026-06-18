## sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/index.go

Purpose: command group definition for `soci index`.

Important APIs/types/functions: `Command` with `listCommand`, `infoCommand`, and `rmCommand`.

Control flow: urfave cli dispatches subcommands; this file performs no data operations itself.

State and persistence: none directly, but subcommands inspect and mutate artifacts DB/content stores.

Dependencies and integration: depends on urfave cli and sibling command implementations.

Risks and test signals: no direct tests; correctness is command registration coverage.
