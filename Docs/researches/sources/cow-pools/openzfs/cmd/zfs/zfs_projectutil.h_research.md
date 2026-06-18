# File Research: sources/cow-pools/openzfs/cmd/zfs/zfs_projectutil.h

Small header for `zfs project` command support.

Defines:
- `zfs_project_ops_t`: operation enum for project handling: default, list, check, clear, and set.
- `zfs_project_control_t`: control structure carrying expected project id plus boolean behavior flags for directory-only traversal, ignoring missing entries, preserving project ids, newline formatting, recursive operation, and setting the project flag.
- `zfs_project_handle(const char *name, zfs_project_control_t *zpc)`: exported entry point for applying the selected project operation to a named path or dataset object.

Role:
- Provides the public command-local interface between `zfs_main.c` style command parsing and project quota/id implementation code.
- The structure is policy/configuration only; no implementation or filesystem mutation is in this header.
