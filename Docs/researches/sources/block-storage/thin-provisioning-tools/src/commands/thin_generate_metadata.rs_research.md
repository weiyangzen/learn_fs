# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_generate_metadata.rs

Development command wrapper for synthetic thin metadata generation and `needs_check` mutation.

CLI:
- Command group: `--format` or `--set-needs-check[=BOOL]`.
- Format options: `--block-size` sectors default 128, `--nr-data-blocks` default 10240.
- Required `--output/-o`.
- Adds version and engine args.

Runtime behavior:
- Parses thin engine options.
- Builds `MetadataOp::Format` or `MetadataOp::SetNeedsCheck`.
- Delegates to `thin::metadata_generator::generate_metadata`.
