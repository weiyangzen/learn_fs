## sources/cloud-native/soci-snapshotter/cmd/soci/main.go

Purpose: entrypoint for the `soci` CLI.

Important APIs/types/functions: `main` builds a `cli.Command` with global flags, version, command groups, and a `Before` hook.

Control flow: register index, ztoc, prefetch, create, convert, push, and rebuild-db commands. Before each command, ensure snapshotter root exists except for standalone convert. Run app with cancellable background context and exit nonzero on error.

State and persistence: may create the snapshotter root path before most commands.

Dependencies and integration: command packages, config/global flags, version metadata, and `soci.EnsureSnapshotterRootPath`.

Risks and test signals: the `Before` hook assumes the nested command lookup for standalone convert is safe. No direct tests for command registration in this subset.
