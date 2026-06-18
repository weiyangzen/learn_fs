# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/node-filesystem-override.yaml

Purpose: Fixture for node-specific filesystem-specific override behavior.

Important data: Top-level default config sets base networking values and management port. A node-specific entry for `testnode` contains `fileSystemSpecificConfigs` for `sysMgmtdHost: 127.0.0.1` with `grpcPort` and `1` variants for networking and port config.

Control flow: For matching node ID, `parseConfigFromFile` merges the node-specific filesystem config into the plugin's filesystem-specific list via `overwriteFileSystemSpecificConfigs`. Because there is no pre-existing filesystem-specific entry for that host, it appends a new entry.

State and persistence: Static fixture.

Dependencies and integration points: Models per-node and per-filesystem config overrides that later get selected by `squashConfigForSysMgmtdHost` for a mounted BeeGFS filesystem.

Risks: If multiple entries target the same `sysMgmtdHost`, merge behavior overwrites fields in place; ordering matters. Top-level `grpcPort` is absent, so tests verify override can introduce it only for the specific filesystem.

Test signals: `TestParseConfigFromFile` expects default config unchanged and one appended filesystem-specific config for `127.0.0.1`.
