# sources/distributed-fs/ceph-client/tools/testing/selftests/watchdog/watchdog-test.c

## Purpose

`watchdog-test.c` is an interactive and scripted watchdog UAPI exerciser. It opens a watchdog device, validates `WDIOC_GETSUPPORT`, allows left-to-right ioctl operations for status, boot status, enable/disable, timeout, pretimeout, time-left, temperature, and info, and can run a keepalive loop until terminated.

## Important APIs, Types, and Functions

The program uses Linux watchdog ioctls from `<linux/watchdog.h>`: `WDIOC_GETSUPPORT`, `WDIOC_KEEPALIVE`, `WDIOC_GETBOOTSTATUS`, `WDIOC_SETOPTIONS`, `WDIOC_GETSTATUS`, `WDIOC_GETTEMP`, `WDIOC_SETTIMEOUT`, `WDIOC_GETTIMEOUT`, `WDIOC_SETPRETIMEOUT`, `WDIOC_GETPRETIMEOUT`, and `WDIOC_GETTIMELEFT`. Command-line parsing is via `getopt_long()` with options such as `--file`, `--info`, `--status`, `--bootstatus`, `--disable`, `--enable`, `--pingrate`, and timeout-related options. `print_status()` and `print_boot_status()` decode status bitmasks. `term()` and the `end` path write the magic close character `V`.

## Control Flow

The first getopt pass extracts the device path, defaulting to `/dev/watchdog`. The program opens it write-only, verifies watchdog support with `WDIOC_GETSUPPORT`, resets `optind`, then processes all options left-to-right so users can disable, reconfigure, and enable in one command. One-shot operations set `oneshot`, causing the program to write `V`, close, and exit. Without a one-shot request, the program requires `WDIOF_KEEPALIVEPING`, registers signal handlers, and loops forever calling `WDIOC_KEEPALIVE` and sleeping `ping_rate` seconds.

## State and Persistence Behavior

The program mutates the system watchdog device. It may enable or disable hardware, change timeout/pretimeout values, and keep the timer alive. On exit and signal handling it writes `V` to request magic close when supported. No local files are persisted.

## Dependencies and Integration Points

It depends on a watchdog device node, sufficient privileges, watchdog core UAPI, and driver support for the requested ioctls. It is designed to run against hardware watchdogs or software watchdogs such as `softdog`.

## Risks and Edge Cases

Misuse can reboot or power-cycle the machine if the watchdog is enabled and not kept alive. `SIGKILL` cannot actually be caught despite being registered. The program opens the device `O_WRONLY`, so driver-specific ioctls must tolerate that. Some status descriptions mix option and status bit namespaces, reflecting historical watchdog API conventions.

## Test Signals

Useful pass signals include successful support validation, correct status/bootstatus decoding, successful enable/disable and timeout operations when supported, expected errors for unsupported ioctls, periodic dots from keepalive, and successful magic-close write on exit.
