# File Research: sources/block-storage/thin-provisioning-tools/src/bin/pdata_tools_dev.rs

Development-tool multiplexer binary. It mirrors `pdata_tools.rs` but only exposes dev/debug commands gated elsewhere by feature configuration.

Key behavior:
- Registers synthetic metadata and damage-generation commands: `era_generate_metadata`, `cache_generate_metadata`, `cache_generate_damage`, `thin_generate_metadata`, `thin_generate_damage`.
- Registers exploratory/stat tooling: `thin_explore` and `thin_stat`.
- Strips the `pdata_tools_dev` executable basename and dispatches on the next basename.
- Emits usage and `exitcode::USAGE` for missing or unknown commands.

This file is intentionally small and delegates all command-specific parsing and execution to `thinp::commands::*`.
