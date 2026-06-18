## sources/cloud-native/soci-snapshotter/config/config.toml

Purpose: sample/default TOML configuration for soci-snapshotter-grpc.

Important settings: covers top-level metrics/debug/metadata flags, HTTP retry/timeout config, blob fetch settings, directory cache behavior, FUSE timeouts, background fetch, content store selection, prefetch, pull modes, keychains, resolver, and snapshotter mount policy.

Control flow: consumed by `config.NewConfigFromToml`; values are decoded into `Config` then normalized by parser functions.

State and persistence: no runtime state itself; selecting stores, paths, and pull modes affects daemon persistence and network behavior.

Dependencies and integration: mirrors TOML tags across `config` package structs.

Risks and test signals: this file sets content store type to `soci`, while `DefaultContentStoreType` constant is `containerd` for CLI default and parser default is SOCI when empty, so readers must distinguish sample config from CLI defaults. Tests validate parser behavior, not this exact file.
