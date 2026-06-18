# File Research: sources/block-storage/lvm2/tools/lvreduce.c

## Purpose
Thin wrapper implementing the legacy command-name entry for `lvreduce`.

## Main Behavior
- `lvreduce()` directly delegates to `lvresize_cmd(cmd, argc, argv)`.

## Important Details
- Actual reduce semantics are selected by generated command enum inside `lvresize.c`.
- This file exists to preserve the command-name function hook.
