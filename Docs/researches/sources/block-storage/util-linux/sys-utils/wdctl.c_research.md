# File Research: sources/block-storage/util-linux/sys-utils/wdctl.c

This file implements `wdctl(8)`, a watchdog status/configuration utility. It reads watchdog identity, options, status, boot status, timeouts, time left, pretimeout governor data, and can set timeout, pretimeout, or pretimeout governor.

Watchdog flags are described by `wdflags[]`, and output columns by `infos[]`. `show_flags()` renders supported watchdog option bits with libsmartcols, including current status and boot-status bit values. `print_device()` chooses between pretty multi-line output, one-line `NAME=value` output, and optional flag tables depending on `struct wd_control`.

Device discovery prefers `/dev/watchdog0` over legacy `/dev/watchdog`. `get_sysfs()` resolves the character device through `/sys/dev/char/<major>:<minor>` and requires an `identity` attribute before treating sysfs as usable. The `struct wd_device` stores sysfs context, watchdog info, timeouts, governor strings, status bitmasks, and booleans describing which fields were successfully read.

The file is careful with watchdog device opens. `set_watchdog()` and `read_watchdog_from_device()` block signals while the watchdog fd is open, avoid `err()`/`exit()` in the critical section, write the magic close character `V` in a retry loop, and then close the fd to avoid unintentionally arming a reboot. Setting timeouts uses `WDIOC_SETTIMEOUT` and `WDIOC_SETPRETIMEOUT`; setting the pretimeout governor writes the sysfs `pretimeout_governor` attribute.

`read_watchdog_from_sysfs()` is preferred and reads identity, firmware version, options, status, bootstatus, nowayout, timeout, pretimeout, and timeleft. `should_read_from_device()` avoids opening the device when sysfs has enough data or `nowayout` is set, falling back to ioctl reads only when needed. `read_governors()` parses `pretimeout_available_governors` and current `pretimeout_governor`.

`main()` parses output filters, column selection, hide/raw/oneline modes, set operations, and target devices. It initializes default flag columns, picks the default device if none is supplied, optionally applies requested settings, reads the watchdog, prints the requested view, releases sysfs path context, and returns failure if any device operation failed.
