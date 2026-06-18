# File Research: sources/block-storage/thin-provisioning-tools/src/commands/era_generate_metadata.rs

Development command wrapper for synthetic era metadata creation.

CLI:
- Required command `--format`.
- Options: `--block-size` sectors default 128, `--nr-blocks` default 10240, `--current-era` default 0, `--nr-writesets` default 0.
- Required `--output/-o`.
- Adds version and engine args.

Runtime behavior:
- Parses era engine options.
- Builds `MetadataOp::Format(EraFormatOpts)`.
- Delegates to `era::metadata_generator::generate_metadata`.
