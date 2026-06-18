## sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/ztoc.go

Purpose: command group definition for `soci ztoc`.

Important APIs/types/functions: `Command` with `infoCommand`, `getFileCommand`, and `listCommand`.

Control flow: no logic beyond registering subcommands.

State and persistence: none directly; subcommands read zTOC and layer artifacts and may write an extracted file.

Dependencies and integration: urfave cli and sibling zTOC command implementations.

Risks and test signals: no direct tests; registration bugs would hide subcommands from the CLI.
