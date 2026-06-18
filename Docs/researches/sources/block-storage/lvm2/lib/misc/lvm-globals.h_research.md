# File Research: sources/block-storage/lvm2/lib/misc/lvm-globals.h

This header declares global runtime setting APIs.

Content:
- Defaults: `VERBOSE_BASE_LEVEL`, `SECURITY_LEVEL`, `PV_MIN_SIZE_KB`.
- Setter/getter prototypes for logging, filtering, test mode, dmeventd, udev, activation, memory, command name, and misc behavior.
- Defines `DMEVENTD_MONITOR_IGNORE` as `-1`.

Dependencies:
- `<stdint.h>` and forward-declared `enum dev_ext_e`.

Role:
- Shared interface for process-global LVM state.
