# File Research: sources/cow-pools/bcachefs-tools/src/commands/subvolume.rs

## Purpose
Implements `bcachefs subvolume` command group for creating, deleting, snapshotting, listing subvolumes, and listing snapshot usage/tree information.

## Main Interfaces
- CLI struct: `Cli`
- Subcommand enum: `Subcommands`
- Command export: `CMD = typed_cmd!("subvolume", ..., aliases: ["subvol"], ...)`
- Core helpers:
  - `bcachefs_ioctl`
  - `bcachefs_flex_ioctl`
  - `subvol_readdir`
  - `subvol_to_path`
  - `query_snapshot_tree`
  - `compute_subvol_sizes`
  - listing/printing helpers for flat, tree, and JSON output.

## Behavior
- `create` creates one or more subvolumes at target paths.
- `delete` canonicalizes and deletes target subvolumes.
- `snapshot` creates a COW snapshot, optionally read-only, with optional source path.
- `list` supports flat, recursive, tree, JSON, snapshot inclusion, read-only filtering, and sorting by name/size/time.
- `list-snapshots` supports tree, flat, JSON, read-only filtering, and sorting for flat output.
- Uses kernel ioctls for subvolume listing, subvolume ID to path, and snapshot tree usage.
- Calculates cumulative subvolume size by walking from each snapshot node up through ancestors.
- Formats flags, timestamps, human-readable sizes, snapshot-parent relationships, and nested children.

## Dependencies and Coupling
- Uses `BcachefsHandle` for create/delete/snapshot operations.
- Uses ioctl numbers:
  - `BCH_IOCTL_SUBVOLUME_LIST = 31`
  - `BCH_IOCTL_SUBVOLUME_TO_PATH = 32`
  - `BCH_IOCTL_SNAPSHOT_TREE_USAGE = 33`
- Uses bindgen ioctl structs:
  - `bch_ioctl_snapshot_node`
  - `bch_ioctl_subvol_dirent`
  - `bch_ioctl_subvol_readdir`
- Uses `serde_json` for JSON output and `chrono::Local` for timestamps.

## Important Implementation Notes
- `FlexArrayIoctl` abstracts retrying flexible-array ioctls when the kernel returns `ERANGE`.
- `subvol_readdir` parses variable-length records from a 64 KiB buffer.
- Tree output uses Unicode branch characters.
- Snapshot tree output handles `ENOTTY` by printing that the ioctl is unsupported and returning success.
- Relative create targets are resolved against current directory before opening the containing filesystem.

## Risks and Edge Cases
- `subvol_to_path` uses a fixed 4096-byte buffer.
- Recursive collection ignores errors opening nested subvolumes in `collect_entries`, but JSON recursion propagates errors.
- Tree output uses Unicode despite most Rust files being ASCII.
- `SortBy::Time` is ignored for snapshot flat output.
- Ioctl struct definitions and numbers must match kernel ABI exactly.
