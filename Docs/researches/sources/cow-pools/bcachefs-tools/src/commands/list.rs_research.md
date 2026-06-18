# File Research: sources/cow-pools/bcachefs-tools/src/commands/list.rs

## Purpose
Implements `bcachefs list`, a read-only debug command for listing btree metadata contents, btree node formats, btree node keys, or raw on-disk node representations.

## Main Interfaces
- CLI struct: `Cli`
- Mode enum: `Mode`
- Command export: `CMD = typed_cmd!("list", ...)`
- Listing helpers:
  - `list_keys`
  - `list_btree_formats`
  - `list_btree_nodes`
  - `list_nodes_ondisk`

## Behavior
- Opens devices read-only, no changes, no exclusive lock, no recovery, with degraded and error-continue behavior.
- Optional `--fsck` enables recovery and fixes errors before listing.
- `keys` mode walks btree keys at a selected btree/level/range and optional bkey type.
- `formats` mode prints btree node format details.
- `nodes` mode prints btree node keys.
- `nodes-ondisk` prints raw on-disk node text.
- If the start snapshot is zero, key listing uses `ALL_SNAPSHOTS`.
- Uses `-b`, `-s`, `-e`, `-l`, and `-k` to select btree, range, level, and bkey type.

## Dependencies and Coupling
- Uses bcachefs bindgen parser types for `btree_id`, `bch_bkey_type`, and `bpos`.
- Uses `BtreeIter`, `BtreeNodeIter`, and transaction wrappers.
- Uses `logging::setup` for verbosity/color configuration.

## Important Implementation Notes
- Iteration stops once key/node position exceeds the requested end position.
- Node modes iterate from requested level up to `BTREE_MAX_DEPTH`.
- Output is plain text suitable for debugging and diffing.

## Risks and Edge Cases
- `--fsck` uses `fix_errors=yes`, so a command named `list` can cause repair behavior when requested.
- Large ranges can produce very large output.
- The command depends on textual formatting from bcachefs C/Rust wrappers remaining stable enough for tooling.
