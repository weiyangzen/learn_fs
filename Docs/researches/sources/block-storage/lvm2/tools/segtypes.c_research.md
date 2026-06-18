# File Research: sources/block-storage/lvm2/tools/segtypes.c

## Purpose
`segtypes.c` implements the `segtypes` command.

## Behavior
`segtypes()` ignores positional arguments, calls `display_segtypes(cmd)`, and returns `ECMD_PROCESSED`.

## Integration Notes
The command is a thin CLI wrapper around the segment-type display helper exposed through `tools.h`. It performs no validation or filtering locally.
