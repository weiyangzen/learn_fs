# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_generate_metadata.rs

Development command wrapper for synthetic cache metadata generation and superblock mutation.

CLI command group:
- `--format`.
- `--set-superblock-version NUM`.
- `--set-needs-check[=BOOL]`.
- `--set-clean-shutdown[=BOOL]`.

Format options:
- `--cache-block-size` sectors, default 128.
- `--hotspot-size`, default 1.
- `--nr-cache-blocks`, default 10240.
- `--nr-origin-blocks`, default 1048576.
- `--percent-dirty`, default 50.
- `--percent-resident`, default 80.
- `--metadata-version` restricted to 1 or 2, default 2.
- Required `--output/-o`.

Runtime behavior:
- Parses cache engine options.
- Converts selected operation into `MetadataOp`.
- Delegates to `cache::metadata_generator::generate_metadata`.
