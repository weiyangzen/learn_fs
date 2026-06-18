<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/it8712f_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/it8712f_wdt.c`

Purpose: legacy IT8712F Smart Guardian watchdog driver using Super I/O configuration ports and a game-port "DogFood" address for pinging.

Important APIs, types, and functions: Super I/O helpers enter/exit configuration mode with `request_muxed_region(0x2e, 2)`. `it8712f_wdt_update_margin()` chooses seconds or minutes precision and writes WDT config/timeout bytes. `it8712f_wdt_enable()` selects GPIO LDN, programs control/config, exits, then pings via game-port read. `it8712f_wdt_disable()` clears config/control/timeout registers. Legacy file operations implement magic close and ioctls.

Control flow: init finds the chip ID, activates/reads the game-port base, adjusts max units for later revisions, reserves the ping I/O byte, disables any existing watchdog, registers a reboot notifier, and registers `/dev/watchdog`. Open enforces single-open and enables the watchdog. Writes ping and track `V` magic close. Release disables only with magic close and `!nowayout`. Ioctl supports get status, keepalive, timeout set/get.

State and persistence: driver state is in globals `wdt_open`, `expect_close`, `revision`, `address`, and module parameters. Hardware reset cause is read from `WDT_CONTROL` status bit for `GETSTATUS`, but `GETBOOTSTATUS` always returns zero. Later revisions support 16-bit timeout units.

Dependencies and integration points: depends on x86-style I/O ports, Super I/O IT8712F device ID, game-port LDN activation, misc watchdog ABI, reboot notifier, and legacy user-space magic-close semantics.

Risks and test signals: risks include sharing Super I/O ports, losing the magic-close state, wrong seconds/minutes conversion, and reliance on game-port side-effect pinging. Test chip detection, revision-specific 8/16-bit timeouts, busy I/O regions, WDIOC_SETTIMEOUT bounds, unexpected close, reboot notifier, and status-bit reset cause.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/it8712f_wdt.c -->
