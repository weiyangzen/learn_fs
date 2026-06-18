# Research: sources/distributed-fs/ipfs-kubo/config/plugins.go

Purpose: Defines plugin configuration schema.

Important APIs/types/functions: `Plugins` holds a map of plugin name to `Plugin`; `Plugin` has `Disabled` and arbitrary `Config`.

Control flow, state, and persistence: No functions. Plugin config is persisted and interpreted by plugin loader implementations.

Dependencies and integration points: `commands.Context` holds a plugin loader. `config_test.go` verifies dynamic key validation for `Plugins.Plugins.peerlog.Config.Enabled`.

Risks and test signals: `Config any` intentionally allows arbitrary shape, so validation is limited and plugin-specific. Loader path is omitted for security. Tests cover dynamic key validation but not plugin runtime behavior.
