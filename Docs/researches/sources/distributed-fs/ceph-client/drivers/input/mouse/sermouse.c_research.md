# sources/distributed-fs/ceph-client/drivers/input/mouse/sermouse.c

`sermouse.c` implements an RS-232 serial mouse serio driver for Mouse Systems, Sun, Microsoft, Logitech M+, Microsoft wheel, Logitech wheel-plus, and Logitech MZ++ protocols.

`sermouse_connect()` allocates `struct sermouse` and an input device, names it from the protocol, configures capabilities from `serio->id.extra`, opens serio, and registers input. `sermouse_interrupt()` resets packet assembly after 100 ms idle and dispatches bytes to `sermouse_process_msc()` or `sermouse_process_ms()`. The MSC/Sun path validates first-byte signature and emits predicted movement. The MS/Logitech path handles framing by bit 6, middle-button guessing, protocol promotion, wheel and horizontal wheel packets, side/extra buttons, and partial MZ++ decoding. Disconnect closes serio, unregisters input, and frees state.

State includes byte buffer, count, protocol type, last timestamp, phys path, and input device. Dependencies are serio RS232 protocol IDs and input. Risks are weak framing/noise sensitivity, timing resets, heuristic middle button behavior, partial MZ++ support, and reliance on `id.extra` for capabilities. Test signals include byte-stream decoding per protocol, idle reset, MS-to-MP promotion, wheel/buttons, unknown MZ++ logging, and connect/disconnect cleanup.
