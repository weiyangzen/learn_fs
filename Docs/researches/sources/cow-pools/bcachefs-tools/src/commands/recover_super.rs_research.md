# File Research: sources/cow-pools/bcachefs-tools/src/commands/recover_super.rs

## Purpose
Implements `bcachefs recover-super`, which recovers damaged or overwritten superblocks either by scanning a device for backup superblocks or by rebuilding a member superblock from another member’s superblock.

## Main Interfaces
- CLI struct: `RecoverSuperCli`
- Command export: `CMD = typed_cmd!("recover-super", ...)`
- Key functions:
  - `cmd_recover_super`
  - `recover_from_scan`
  - `recover_from_member`
  - `probe_one_super`
  - `probe_sb_range`
  - `validate_sb`

## Behavior
- Supports explicit device size, explicit probe offset, scan length, source member device plus target dev index, `--yes`, and verbose scanning.
- Scanning mode probes a specific offset when given, otherwise scans from the beginning and end of the device.
- Candidate superblocks are validated with `bch2_sb_validate`.
- Chooses the candidate with the most recent member last-mount time.
- Member-copy mode reads a source filesystem superblock, validates dev index, deletes journal fields, sets target `dev_idx`, and reinitializes the superblock layout for the target device size.
- Prints the recovered superblock text before prompting.
- Writes the recovered superblock when `--yes` is set or the user confirms.
- Runs `udevadm trigger --settle <device>` after writing.
- Warns that member-copy recovery removes the journal and requires fsck.

## Dependencies and Coupling
- Uses custom extern declaration for `bch2_sb_validate` because bindgen enum typing does not accept raw `0`.
- Uses `super_io` magic constants, `vstruct_bytes_sb`, `sb_layout_init`, and `bch2_super_write`.
- Uses C field deletion for journal and journal_v2 fields.
- Uses `Printbuf::sb_to_text`.

## Important Implementation Notes
- Buffer-to-superblock conversion is unsafe and assumes adequate alignment and size.
- Scan offsets are 512-byte aligned.
- Scanning validates magic before computing variable structure length.
- `recover_from_member` copies the source C-allocated superblock into an owned byte buffer before the handle drops.

## Risks and Edge Cases
- `recover_from_scan` computes `dev_size - scan_len`; if scan length exceeds device size this can underflow.
- Candidate validation mutates the buffer through `bch2_sb_validate`.
- The final user prompt uses C `ask_yn`.
- Member-copy mode intentionally removes journal fields, changing recovery requirements.
