# sources/cloud-native/composefs-rs/crates/composefs-storage/src/config.rs

## Purpose
This module parses containers-storage `storage.conf`-style TOML data into Rust structures. It captures the configured driver, primary root, runtime root, additional image stores, and additional layer store settings.

## Important APIs, Types, and Functions
`StorageConfig` has fields `driver`, `root`, `run_root`, `image_stores`, and `layer_stores`, all deserialized with defaults. `AdditionalLayerStore` has `path` and `with_reference`. `StorageConfig::from_toml()` wraps `toml::from_str`.

## Control Flow
There is no complex runtime control flow. Callers pass TOML text to `from_toml()`, serde fills missing fields with defaults, and nested `[[layer_stores]]` entries deserialize into `AdditionalLayerStore` values.

## State and Persistence
The module does not read files itself and stores no global state. It creates an in-memory configuration value from caller-provided content. Path fields are `PathBuf`s and can represent system, user, or additional store locations.

## Dependencies and Integration Points
It depends on `serde::Deserialize`, `toml`, and `PathBuf`. The parsed data is intended to feed storage discovery/opening code, though the current `storage.rs` also has environment/default-root discovery paths.

## Risks
The module does not validate driver values, path existence, or overlay support; it only parses. The documentation examples show `[storage]` tables, but the struct shape as written expects fields at the current TOML level unless callers deserialize a containing type elsewhere. Empty defaults can hide missing configuration unless validation is done by the caller.

## Test Signals
Tests cover basic parsing of `driver` and `root`, and parsing a `[[layer_stores]]` entry with `with_reference = true`. There are no tests for `[storage]` nesting, `image_stores`, `run_root`, invalid TOML, or validation behavior.
