# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_metadata_pack.rs

Command wrapper for packing used thin metadata blocks into a compressed file.

CLI:
- Required `--input/-i DEV`.
- Required `--output/-o FILE`.
- `--force/-f` to skip overwrite confirmation.
- Adds version args.

Runtime behavior:
- Validates input exists, is not tiny, and is not XML.
- Unless forced, calls `check_overwrite_metadata` on output.
- Delegates to `pack::toplevel::pack`.
