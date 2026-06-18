## sources/cloud-native/soci-snapshotter/config/config_test.go

Purpose: verifies config defaults, TOML parsing, decompression stream parsing, parallel fallback settings, and size-string parsing.

Important APIs/types/functions: `TestConfigDefaults`, `TestNewConfigFromToml`, and `TestSizeParser`.

Control flow: default test compares many fields from `NewConfig` with default constants. TOML tests write temporary config files and assert decoded structures or errors. Size parser tests cover units, decimals, spacing, zero, negative, and invalid strings.

State and persistence: uses temporary config files only.

Dependencies and integration: exercises `NewConfigFromToml`, `DefaultPullModes`, parser functions, and `parseSize`.

Risks and test signals: broad default coverage is strong. It does not test default config path missing behavior, content-store socket trimming, or invalid relationships between parallel limits.
