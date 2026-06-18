# File Research: sources/block-storage/lvm2/tools/dumpconfig.c

## Purpose
`dumpconfig.c` implements `dumpconfig`, `config`, and `lvmconfig`. These commands display, validate, or write LVM configuration trees.

## Main Flow
`dumpconfig()` validates option combinations, selects or merges the active config tree, optionally validates it, builds the requested config-definition tree, and writes it through `config_write()`.

## Key Behavior
- `_get_vsn()` parses `--atversion`, `--sinceversion`, or `LVM_VERSION`.
- `_do_def_check()` runs config-definition checks with mode-specific settings.
- `_merge_config_cascade()` recursively merges cascaded config trees.
- `_config_validate()` validates current configuration for `--validate`.

Supported output modes include `list`, `full`, `current`, `missing`, `default`, `diff`, `new`, `profilable`, `profilable-command`, and `profilable-metadata`.

## Integration Notes
The command uses config tree/profile APIs and returns standard LVM command return codes. `config()` and `lvmconfig()` are wrappers around `dumpconfig()`.

## Risks
The option matrix is dense. Future output modes or flags need careful validation against existing incompatibility checks.
