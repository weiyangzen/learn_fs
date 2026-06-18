# File Research: sources/block-storage/lvm2/tools/errors.h

## Purpose
`errors.h` defines integer return codes used by LVM command handlers.

## Values
- `ECMD_PROCESSED`: command completed successfully.
- `ENO_SUCH_CMD`: command was not found.
- `EINVALID_CMD_LINE`: invalid command-line input.
- `EINIT_FAILED`: initialization failed.
- `ECMD_FAILED`: command execution failed.

## Integration Notes
These values are used across CLI command handlers and cmdlib-facing execution paths.
