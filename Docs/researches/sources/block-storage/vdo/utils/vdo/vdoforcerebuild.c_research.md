# File Research: sources/block-storage/vdo/utils/vdo/vdoforcerebuild.c

## Purpose

`vdoforcerebuild.c` implements `vdoforcerebuild`, a small metadata-mutating utility that marks an existing VDO device so it exits read-only mode and attempts metadata regeneration/rebuild.

## Command-Line Interface

Usage:

```text
vdoforcerebuild filename
```

Options documented:

- `--help`
- `--version`

## Main Flow

`main()`:

1. Registers VDO status codes.
2. Parses options.
3. Requires exactly one filename.
4. Creates a writable file layer with `makeFileLayer(filename, 0, &layer)`.
5. Calls `forceVDORebuild(layer)`.
6. Destroys the layer, syncing/closing the backing file.

## Dependencies

Includes:

- System: `err.h`, `getopt.h`, `stdio.h`, `stdlib.h`, `unistd.h`
- Utility: `errors.h`, `logger.h`
- VDO/base: `constants.h`, `status-codes.h`, `types.h`, `vdoConfig.h`
- VDO helper: `fileLayer.h`

## Notable Behaviors and Risks

- The `options` table includes `--version` mapped to `'V'`, but `optionString` is `"h"` and omits `V`. Long `--version` works through `getopt_long()`, but short `-V` is not accepted despite the handler.
- This tool writes metadata state. It does not use `makeVDOFromFile()` because it operates directly through the physical layer and `forceVDORebuild()`.
- Failure exits use status/result values through `errx()`.
