# sources/distributed-fs/ceph-client/drivers/watchdog/pcwd.c

## Purpose
`pcwd.c` is the Berkshire ISA-PC Watchdog driver. It auto-detects legacy ISA cards by heartbeat bits, handles Rev A and Rev C differences, provides `/dev/watchdog`, and optionally exposes `/dev/temperature`.

## Important APIs, types, and functions
The global `pcwd_private` holds firmware string, revision, temperature support, command mode, boot status, I/O address, lock, timer, and next heartbeat. Important routines include `pcwd_isa_match`, `pcwd_isa_probe`, `send_isa_command`, `set_command_mode`, `pcwd_timer_ping`, `pcwd_start`, `pcwd_stop`, `pcwd_keepalive`, `pcwd_set_heartbeat`, status/temperature helpers, file operations, and ISA remove/shutdown.

## Control flow
ISA match reserves candidate ports and watches Rev A/Rev C heartbeat bits. Probe claims the region, determines revision, reads and clears boot status, initializes a kernel timer, disables the board, probes temperature support, logs firmware/switch info, picks heartbeat from module parameter or DIP switches, registers optional temperature and watchdog miscdevices. Open starts the board and timer; timer pings hardware only while userspace has refreshed `next_heartbeat`; write/ioctl keepalives extend that deadline. Close stops only after magic `V`; otherwise the timer continues toward reset.

## State and persistence
Runtime state is global because `/dev/watchdog` supports one card. Hardware boot/trip bits can survive reset until cleared. The driver keeps a software timer layered over the hardware timer to translate userspace heartbeat policy into frequent hardware pings.

## Dependencies and integration points
It integrates ISA driver probing, I/O ports, timers, miscdevices, classic watchdog ioctls, optional temperature minor, kernel poweroff on temperature panic, and module parameters `debug`, `heartbeat`, and `nowayout`.

## Risks and test signals
Risks include legacy probing false positives, timer-delete races, command-mode/temperature read conflicts, copy-to-user of only one byte for temperature, one-card global state, and `WDIOC_SETOPTIONS` returning `-EINVAL` even after handling options in some paths. Test signals include all ISA port candidates, Rev A vs Rev C, DIP-switch heartbeat, timer heartbeat loss, magic-close, temperature support, bootstatus clear, and remove/shutdown behavior.
