# File Research: sources/block-storage/lvm2/lib/misc/intl.h

This header defines LVM’s translation macro.

Behavior:
- If `INTL_PACKAGE` is defined, includes `<libintl.h>` and maps `_()` to `dgettext(INTL_PACKAGE, String)`.
- Otherwise `_()` returns the original string.

Role:
- Central conditional gettext support used through `lib.h`.

Risk:
- `_` is a global macro name; including order matters for files that may define their own `_`.
