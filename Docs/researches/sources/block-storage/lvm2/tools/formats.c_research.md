# File Research: sources/block-storage/lvm2/tools/formats.c

## Purpose
`formats.c` implements the `formats` command, which lists available LVM metadata formats.

## Behavior
`formats()` ignores positional arguments, calls `display_formats(cmd)`, and returns `ECMD_PROCESSED`.

## Integration Notes
The command is registered as read-only and metadata-free in `commands.h`.
