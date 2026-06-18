# sources/cloud-native/ostree/src/ostree/ot-builtin-summary.c

## Purpose
Implements `ostree summary`, updating repository summary metadata and viewing or querying the local summary file.

## Important APIs, Types, And Functions
`ostree_builtin_summary()` is the entry point. `build_additional_metadata()` parses `KEY=VALUE` arguments as GVariant text into an `a{sv}` dictionary. `get_summary_data()` reads the repo's `summary` file as `GBytes`. The command uses `ostree_repo_regenerate_metadata()`, `ot_dump_summary_bytes()`, `ot_dump_summary_metadata_keys()`, and `ot_dump_summary_metadata_key()`.

## Control Flow
The command initializes signapi when `--sign` keys are supplied. In update mode it requires repo writability, parses optional additional metadata, builds metadata options for GPG key IDs, GPG homedir, signapi secret keys, and sign type, then regenerates repository metadata. View/raw mode reads the summary file and dumps it, with raw mode setting `OSTREE_DUMP_RAW`. Metadata list and print modes read the summary and delegate to dump helpers. If no operation option is supplied, it returns an error asking for `-u`.

## State And Persistence
Update mode writes or replaces summary metadata and signatures. View, raw, list-metadata-keys, and print-metadata-key are read-only. Additional metadata becomes part of the regenerated summary.

## Dependencies And Integration Points
This file connects repository summary generation, GPG signing, signapi signing, raw summary parsing, and user-facing dump helpers. Summary files are consumed by remote clients, find-remotes, pull, static delta discovery, and create-usb.

## Risks And Edge Cases
Additional metadata values must parse as GVariant text, not plain strings. Multiple operation flags are resolved by if/else order, with update taking precedence. `get_summary_data()` reads the `summary` file directly via `repo_dir_fd`, so missing summaries produce open errors. The local `OstreeSign *sign` is only used to validate sign type existence; actual signing options are passed to repo metadata generation.

## Test Signals
Tests should cover update with no metadata, update with additional metadata, GPG and signapi signing options, view and raw output, missing summary errors, listing and printing metadata keys, invalid `KEY=VALUE`, invalid variant values, and no-option error behavior.
