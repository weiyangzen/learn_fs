# sources/distributed-fs/ceph-client/drivers/input/misc/yealink.h

## Purpose
`yealink.h` defines the Yealink USB-P1K control-packet ABI and the macro-expanded LCD segment/icon map used by `yealink.c`.

## Important APIs, Types, and Functions
`struct yld_ctl_packet` is the packed 16-byte USB control payload with command, size, big-endian offset, 11 data bytes, and checksum. Command constants include `CMD_INIT`, `CMD_KEYPRESS`, `CMD_SCANCODE`, `CMD_LCD`, `CMD_LED`, `CMD_RING_VOLUME`, `CMD_RING_NOTE`, `CMD_RINGTONE`, and `CMD_DIALTONE`. When included with `_SEG` and `_PIC` defined, the header emits LCD segment and pictogram map entries plus line offsets and sizes.

## Control Flow
There are no functions. The first include provides packet and command definitions. The second include from inside `lcdMap[]` in `yealink.c` expands the LCD layout into map entries, then undefines `_SEG` and `_PIC`. Packet commands are filled by `yealink.c` and sent over USB control transfers.

## State and Persistence Behavior
The header owns no runtime state. It defines the wire layout for state that persists on the phone: LCD bytes, LED state, ringtone/dialtone state, ringtone notes, and key polling/scancode requests.

## Dependencies and Integration Points
It depends on Linux integer types, big-endian annotation, and compile-time `_SEG`/`_PIC` macro definitions. Its constants are tightly coupled to `struct yld_status`, `lcdMap[]`, and `yealink_cmd()` checksum/control-transfer logic in `yealink.c`.

## Risks and Edge Cases
The header is intentionally dual-use: ordinary include guard covers packet definitions, while the LCD map is outside the guard and only expands when macros are defined. Moving the map inside the guard would break the second include. The packed packet layout and checksum size must remain exactly aligned with device firmware. LCD offsets and masks must match `struct yld_status` byte layout.

## Test Signals
Test compile expansion of both include modes, `sizeof(struct yld_ctl_packet) == 16`, command packet formation, LCD line offsets/sizes, all icon names, and visible LCD updates for representative segment characters.
