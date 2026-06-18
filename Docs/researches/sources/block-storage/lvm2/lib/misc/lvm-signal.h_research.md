# File Research: sources/block-storage/lvm2/lib/misc/lvm-signal.h

This header declares signal helper APIs:
- `sigint_allow()`, `sigint_restore()`, `sigint_caught()`, `sigint_clear()`, `sigint_usleep()`.
- `block_signals()`, `unblock_signals()`.

Dependencies:
- `<stdint.h>`, `<unistd.h>` for `useconds_t`.

Role:
- Shared interrupt/signal control interface for locking and activation paths.
