# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_stat.rs

Development command wrapper for thin metadata statistics.

CLI:
- `--op`, default `data_blocks`.
- Supported operations: `data_blocks`, `metadata_blocks`, `data_run_len`.
- Required positional input.
- Adds version and engine args.

Runtime behavior:
- Parses thin engine options.
- Maps operation string to `StatOp`.
- Delegates to `thin::stat::stat`.
- Unknown operation returns `exitcode::USAGE`.
