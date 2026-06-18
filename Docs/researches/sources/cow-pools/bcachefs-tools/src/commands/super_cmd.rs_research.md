# File Research: sources/cow-pools/bcachefs-tools/src/commands/super_cmd.rs

## Purpose
Implements `bcachefs show-super`, which prints bcachefs superblock information from a device, with field filtering and layout display support.

## Main Interfaces
- CLI struct: `ShowSuperCli`
- Command export: `CMD = typed_cmd!("show-super", ...)`
- Main handler: `cmd_show_super`

## Behavior
- Supports `--fields` with comma-separated superblock field names or `all`.
- Supports `--field-only` for scripting a single field without a header.
- Supports `--layout` to print superblock layout.
- Opens the device with `noexcl`, `nochanges`, `no_version_check`, and `nostart`.
- Iterates online members and prints each per-device superblock.
- By default prints `ext`, `members_v1` or `members_v2`, and `errors` fields.
- Uses `sb_to_text_with_names` to format selected fields.

## Dependencies and Coupling
- Uses C flag parsers:
  - `bch2_read_flag_list`
  - `match_string`
- Uses `bch2_sb_fields` table.
- Uses `Fs::open` and `for_each_online_member`.
- Uses per-device `ca.disk_sb.sb`, not filesystem-level `c->disk_sb.sb`.

## Important Implementation Notes
- The file documents why per-device superblocks are used: filesystem-level copies omit fields such as magic and layout.
- Help flag is manually enabled with `disable_help_flag = true` plus an explicit hidden field.

## Risks and Edge Cases
- Invalid field names are fatal.
- Output can include multiple member superblocks when multiple devices are online.
- Field bitmask is u32, so it assumes field IDs fit that width.
