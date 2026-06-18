## sources/cloud-native/soci-snapshotter/cmd/soci/commands/global/global.go

Purpose: defines shared CLI flags for the `soci` command.

Important APIs/types/functions: constants for `address`, `namespace`, `timeout`, `debug`, `content-store`, and `root`, plus `Flags`.

Control flow: no runtime logic beyond flag declarations. Defaults use containerd default address, containerd default namespace, default content store type, and snapshotter root path.

State and persistence: flag values drive later command context, client connections, content-store selection, and root DB/store paths.

Dependencies and integration: config defaults, containerd defaults/namespaces, and urfave cli flag sources from env vars.

Risks and test signals: content-store accepts arbitrary strings at flag level; validation happens later in store creation. No direct tests for global flags.
