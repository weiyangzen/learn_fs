# File Research: sources/cow-pools/bcachefs-tools/src/commands/recovery_pass.rs

## Purpose
Implements `bcachefs recovery-pass`, a superblock-editing command for listing, scheduling, and descheduling required recovery passes.

## Main Interfaces
- CLI struct: `RecoveryPassCli`
- Command export: `CMD = typed_cmd!("recovery-pass", ...)`
- Main handler: `cmd_recovery_pass`

## Behavior
- Parses `--set` and `--unset` recovery pass flag lists using the C recovery-pass name table.
- Converts pass masks to stable on-disk numbering before modifying the superblock extension field.
- Opens the filesystem with `nostart`.
- Gets or creates the `bch_sb_field_ext` field.
- Updates `recovery_passes_required[0]` by clearing unset bits and setting requested bits.
- Writes the superblock if changes were requested.
- Prints scheduled recovery passes using the C bitflag printer, or `(none)`.

## Dependencies and Coupling
- Uses `read_flag_list` with `c::bch2_recovery_passes`.
- Uses C conversions:
  - `bch2_recovery_passes_to_stable`
  - `bch2_recovery_passes_from_stable`
- Uses `sb_field_get_minsize` and `wrappers::sb_lock`.

## Important Implementation Notes
- The lock guard is explicitly dropped before formatting output.
- Only the first u64 of `recovery_passes_required` is modified.

## Risks and Edge Cases
- Multiword recovery-pass masks would require extending beyond `[0]`.
- The command writes superblock state directly and assumes the filesystem is not started.
