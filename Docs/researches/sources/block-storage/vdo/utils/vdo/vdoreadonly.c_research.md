# File Research: sources/block-storage/vdo/utils/vdo/vdoreadonly.c

## Purpose

`vdoreadonly.c` implements `vdoreadonly`, a small metadata-mutating utility that forces an existing VDO device into read-only mode.

## Command-Line Interface

Usage:

```text
vdoreadonly filename
```

Options documented:

- `--help`
- `--version`

## Main Flow

`main()`:

1. Registers status codes.
2. Parses options.
3. Requires exactly one filename.
4. Opens a writable file layer with `makeFileLayer(filename, 0, &layer)`.
5. Calls `setVDOReadOnlyMode(layer)`.
6. Destroys the layer to close and sync.

## Dependencies

Includes:

- System: `err.h`, `getopt.h`, `linux/fs.h`, `stdlib.h`, `sys/ioctl.h`
- Utility: `errors.h`, `fileUtils.h`, `logger.h`, `string-utils.h`
- VDO/base: `constants.h`, `status-codes.h`
- VDO helpers: `fileLayer.h`, `physicalLayer.h`, `vdoConfig.h`, `vdoVolumeUtils.h`

## Notable Behaviors and Risks

- As with `vdoforcerebuild.c`, the options table includes `--version`, but `optionString` is `"h"` and omits short `V`; long `--version` works, short `-V` likely does not.
- Several included headers are not directly used by this file but may reflect shared utility template usage.
- This tool intentionally writes metadata and should only be run against the intended backing device.
