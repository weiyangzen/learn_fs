# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_repair.rs

Command wrapper for `cache_repair`.

CLI:
- Required `--input/-i FILE`.
- Required `--output/-o FILE`.
- `--quiet`.
- Hidden dummy positional for `lvconvert` compatibility.
- Adds verbose, version, and engine args.

Runtime behavior:
- Builds report and parses verbosity.
- Validates input exists, is not tiny, and output exists/is large enough.
- Parses cache engine options.
- Constructs `CacheRepairOptions` and delegates to `cache::repair::repair`.
