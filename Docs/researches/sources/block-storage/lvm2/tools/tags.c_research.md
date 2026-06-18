# File Research: sources/block-storage/lvm2/tools/tags.c

## Purpose
`tags.c` implements the `tags` command.

## Behavior
`tags()` ignores positional arguments, calls `display_tags(cmd)`, and returns `ECMD_PROCESSED`.

## Integration Notes
The command is a simple read-only display wrapper around the tag display helper from the tools layer.
