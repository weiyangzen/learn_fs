# sources/distributed-fs/ceph-client/drivers/watchdog/cgbc_wdt.c

## Purpose
`cgbc_wdt.c` exposes the Congatec Board Controller watchdog through the Linux watchdog core. It sends packed command frames to the parent CGBC MFD command interface and supports optional pretimeout behavior.

## Important APIs, types, and functions
`struct cgbc_wdt_data` links the parent `cgbc_device_data` with a `watchdog_device`. `struct cgbc_wdt_cmd_cfg` is the packed 15-byte command payload validated by `static_assert`. Watchdog ops are `cgbc_wdt_start`, `cgbc_wdt_stop`, `cgbc_wdt_keepalive`, `cgbc_wdt_set_timeout`, and `cgbc_wdt_set_pretimeout`.

## Control Flow
Probe obtains parent MFD data, initializes timeout limits, applies module parameters, and registers the device. Start computes timeout1 as `timeout - pretimeout` in milliseconds and timeout2 as pretimeout in milliseconds, encodes action bytes for reset-only or SMI-plus-reset, and sends `CGBC_WDT_CMD_INIT`. Ping sends `CGBC_WDT_CMD_TRIGGER`; stop sends an init command with disable mode. Timeout/pretimeout changes restart hardware when active.

## State and Persistence
The driver keeps only current watchdog core timeout/pretimeout and a parent pointer. Hardware state lives in the board controller and is updated by command messages. No persistent storage is used.

## Dependencies and Integration Points
It depends on `linux/mfd/cgbc.h`, the parent CGBC command transport, the platform bus, module parameters, and watchdog core pretimeout support.

## Risks and Test Signals
Risks include millisecond overflow/truncation into three-byte fields, pretimeout greater than timeout, command transport failure, and action encoding mismatches with firmware expectations. Tests should cover disabled, reset-only, and SMI pretimeout modes; module parameter parsing; active timeout changes; command payload byte order; and parent command error propagation.
