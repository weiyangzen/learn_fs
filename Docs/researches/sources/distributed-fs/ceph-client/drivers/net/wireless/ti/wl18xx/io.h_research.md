# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/io.h

## Purpose
Declares WiLink 8 top-register 16-bit access helpers.

## Important APIs, types, and functions
- `wl18xx_top_reg_write()` and `wl18xx_top_reg_read()` are marked `__must_check` so callers handle hardware I/O errors.

## Control flow
No executable flow.

## State and persistence behavior
No local state. Implementations mutate or read hardware top registers.

## Dependencies and integration points
Uses `struct wl1271` from wlcore context. Included by `wl18xx/main.c` and `wl18xx/io.c`.

## Risks and test signals
Risk is ignored return values or prototype drift. Build warnings enforce `__must_check`; boot clock setup is the primary runtime signal.
