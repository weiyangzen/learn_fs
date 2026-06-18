## sources/cloud-native/soci-snapshotter/config/config.go

Purpose: root configuration model and TOML loading/defaulting entrypoints.

Important APIs/types/functions: `Config`, `NewConfig`, `NewConfigFromToml`, `parseConfig`, `parseRootConfig`, and default path constants.

Control flow: `NewConfig` initializes defaults that differ from zero values, then runs root/service/fs/parallel parsers. `NewConfigFromToml` returns defaults when the default config path is absent, otherwise decodes TOML over defaults and reparses normalization/default logic.

State and persistence: reads a TOML file; no writes.

Dependencies and integration: embeds `ServiceConfig`, used by daemon startup and config dump/default commands.

Risks and test signals: `NewConfig` returns nil if parser errors, though current defaults should not error. Tests cover defaults, empty TOML, and parse failures for chunk size.
