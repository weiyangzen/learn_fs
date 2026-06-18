# File Research: sources/cow-pools/bcachefs-tools/src/commands/kill_btree_node.rs

## Purpose
Implements `bcachefs kill_btree_node`, a debug/testing command that intentionally corrupts selected btree nodes on disk by overwriting block-sized regions with zeroes.

## Main Interfaces
- CLI struct: `KillBtreeNodeCli`
- Command export: `CMD = typed_cmd!("kill_btree_node", ...)`
- Key helpers:
  - `parse_kill_node`
  - `cmd_kill_btree_node`

## Behavior
- Accepts one or more node specs as `btree:level:idx`, with default level `0` and index `0` if omitted.
- Opens the filesystem read-only through `device_scan::open_scan`.
- Iterates btree nodes at the requested btree and level.
- Finds the Nth matching node, then overwrites each matching pointer replica with a zeroed aligned block.
- Optional `--dev` restricts corruption to one device index; otherwise all replicas are targeted.
- Errors if no nodes are specified or a requested node index is not found.

## Dependencies and Coupling
- Uses `BtreeNodeIter`, `BtreeTrans`, `BkeySC`, and extent pointer extraction via `bkey_ptrs`.
- Uses raw block-device fd from `ca.disk_sb.bdev.bd_fd`.
- Depends on block size from `(*fs.raw).opts.block_size`.

## Important Implementation Notes
- Uses `posix_memalign` because bcachefs block-device fds may be opened with O_DIRECT.
- Writes one block of zeroes at `ptr.offset() << 9`.
- Frees the aligned buffer on normal completion and on not-found failure.

## Risks and Edge Cases
- This is deliberately destructive.
- Partial or failed `pwrite` only logs an error and continues.
- The node spec parser expects numeric/parsable btree IDs according to bindgen parser behavior.
- A panic or unexpected early return before explicit free could leak the aligned buffer.
