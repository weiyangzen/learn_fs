# sources/distributed-fs/moosefs/mfsmaster/changelog.h

This header exposes the master changelog API and annotates formatted logging calls for compiler printf checking.

It defines `PRINTF_LIKE`, rotate flags `ROTATE_FLAG_BROADCAST` and `ROTATE_FLAG_FOREGROUND`, and declares old-change replay, minimum-version lookup, rotation, metadata-restore logging, formatted logging, gid/name formatting helpers, initialization, log version probes, and changelog filename validation.

Mutation code calls `changelog(format, ...)`; restore paths can call `changelog_mr(version, data)` when version is already known; maintenance code calls `changelog_rotate`; metadata-log serving code calls replay helpers.

The header exposes no direct state, but functions operate on process-global changelog retention, file handles, and background saver state. It includes `<inttypes.h>` and is used broadly by metadata mutation modules.

Risks include static-buffer ownership for formatting helpers, bit-field rotate flags without a strong type, and reliance on callers respecting printf formats. Test signals are compiler format warnings, broad consumer builds, replay tests, and rotation tests.
