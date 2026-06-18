# sources/distributed-fs/ceph-client/drivers/watchdog/nct6694_wdt.c

## Purpose
`nct6694_wdt.c` provides watchdog support for the Nuvoton NCT6694 USB-attached MFD device. It sends packed setup and command messages through the parent NCT6694 transport.

## Important APIs, types, and functions
Packed protocol types are `struct nct6694_wdt_setup`, `struct nct6694_wdt_cmd`, and `union nct6694_wdt_msg`. `struct nct6694_wdt_data` stores the watchdog, parent MFD pointer, message buffer, and allocated watchdog index. Operations include `nct6694_wdt_setting`, `start`, `stop`, `ping`, `set_timeout`, `set_pretimeout`, and `get_timeleft`.

## Control flow
Probe gets parent `struct nct6694`, allocates a message buffer, allocates a watchdog slot from `nct6694->wdt_ida`, seeds timeout/pretimeout from module parameter arrays, applies `nowayout`, and registers the watchdog. Start writes setup values in milliseconds with GPO actions. Stop sends command `"WDTC"`; ping sends `"WDTS"`. `get_timeleft` reads the setup message and returns countdown milliseconds divided by 1000.

## State and persistence
Runtime state is per-platform-device but the USB/MFD hardware owns countdown and action state. The IDA allocation persists only for the device lifetime and is devm-freed. There is no bootstatus handling.

## Dependencies and integration points
It depends on `linux/mfd/nct6694.h`, parent driver `nct6694_write_msg/read_msg`, platform child device `nct6694-wdt`, IDA allocation, module parameter arrays for up to two watchdogs, and watchdog pretimeout APIs.

## Risks and test signals
Risks include concurrent reuse of the single message buffer if watchdog core invokes operations concurrently, index values exceeding the two-element module arrays, pretimeout validation only warning on an inverted relationship, and transport errors leaving software timeout fields unchanged or stale. Test signals include dual-device probe, IDA cleanup, USB transport read/write failure, timeout/pretimeout programming, stop/ping command bytes, and countdown readback.
