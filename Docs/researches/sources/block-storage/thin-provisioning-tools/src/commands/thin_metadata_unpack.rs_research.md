# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_metadata_unpack.rs

Command wrapper for unpacking compressed thin metadata into a binary metadata device/file.

CLI:
- Required `--input/-i FILE`.
- Required `--output/-o DEV`.
- `--force/-f` to skip overwrite confirmation.
- Adds version and engine args, though unpack delegates directly to pack layer.

Runtime behavior:
- Validates input exists.
- Unless forced, prompts if output appears to already contain metadata.
- Delegates to `pack::toplevel::unpack`.
