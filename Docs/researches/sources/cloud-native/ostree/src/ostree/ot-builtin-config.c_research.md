# sources/cloud-native/ostree/src/ostree/ot-builtin-config.c

## Purpose
Implements `ostree config`, a small CLI for reading and mutating repository configuration keys. It supports `get`, `set`, and `unset` operations using either `section.key` syntax or an explicit `--group` option.

## Important APIs, Types, And Functions
`ostree_builtin_config()` is the entry point. `split_key_string()` validates and splits `section.key` inputs. The command uses `OstreeRepo`, `GKeyFile`, `ostree_repo_get_config()`, `ostree_repo_copy_config()`, `ostree_repo_write_config()`, and `ostree_repo_write_config_and_reload()`.

## Control Flow
After option parsing, the command requires an operation argument and computes the allowed argument count, with `set` needing one extra value. For `set`, it resolves the group/key pair, copies the repository config, writes the string value, and writes plus reloads the repository config. For `get`, it reads the active config and prints the string value. For `unset`, it copies config, removes the key, ignores missing group/key errors, and writes the config only when removal actually occurred. Unknown operations are reported as errors.

## State And Persistence
`set` persists changes to the repository config and reloads it into the repo object. `unset` persists only when a key was found and removed; missing keys leave disk unchanged. `get` is read-only. The file does not manage transactions because repository config writes are separate from object/ref transactions.

## Dependencies And Integration Points
The command depends on GLib `GKeyFile`, shared option parsing, and repository config helpers. The config it edits is consumed by remote setup, collection IDs, pull behavior, summary generation, signing configuration, and other libostree features.

## Risks And Edge Cases
The argument-count check only rejects too many arguments; each operation has its own missing-argument checks. Without `--group`, keys must contain a dot. Values are always strings, so non-string typed config data is not modeled here. `unset` uses `ostree_repo_write_config()` rather than write-and-reload, so callers relying on immediate in-memory reload behavior should verify the broader repo API expectations.

## Test Signals
Tests should cover set/get/unset with and without `--group`, invalid key syntax, missing operation or arguments, unknown operation, missing key removal being nonfatal, and persistence across reopening the repository.
