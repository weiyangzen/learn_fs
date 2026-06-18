# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_shrink.rs

Command wrapper for shrinking inactive thin pool metadata/data.

CLI:
- Required XML/binary input `--input/-i`.
- Required output `--output/-o`.
- Required data device `--data`.
- Required new pool size `--nr-blocks`.
- `--no-copy` to skip data movement.
- `--binary` to perform binary metadata rebuild rather than XML rewrite.
- Adds version args.

Runtime behavior:
- Parses into `ThinShrinkOptions`.
- Always validates input path.
- In binary mode, also requires non-tiny input and valid output metadata file.
- If copying is enabled, validates data device path.
- Delegates to `thin::shrink::shrink`.

Header comment credits prior Python implementation by Nikhil Kshirsagar.
