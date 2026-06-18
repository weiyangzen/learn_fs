<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/led_hw_brightness_mon.c -->
# sources/distributed-fs/ceph-client/tools/leds/led_hw_brightness_mon.c

## Purpose
`led_hw_brightness_mon.c` is a small userspace diagnostic tool for LED class devices. It monitors the sysfs `brightness_hw_changed` attribute for one LED device and prints a monotonic timestamp plus the new brightness value whenever hardware or firmware changes the LED brightness outside normal kernel control.

## Important APIs, types, and functions
The only entry point is `main()`. It uses `LED_MAX_NAME_SIZE` from `<linux/uleds.h>` for path sizing, constructs `/sys/class/leds/<device>/brightness_hw_changed`, opens it read-only, primes the fd with an initial `read()`, waits with `poll(POLLPRI)`, timestamps with `clock_gettime(CLOCK_MONOTONIC)`, reads the ASCII brightness value into `buf`, rewinds with `lseek()`, and prints `atoi(buf)`.

## Control flow
The tool validates that exactly one device-name argument was provided, opens the sysfs notification file, then enters an infinite blocking poll loop. Each priority event is treated as a brightness-change notification. On poll, read, or seek failure, it breaks out, closes the fd, and returns the last error-ish integer.

## State and persistence behavior
There is no persistent state. Runtime state is the sysfs fd, the current poll descriptor, a short input buffer, and the last timestamp. The initial read is intentionally allowed to fail because it only suppresses stale/spurious notifications when a previous hardware event is already latched.

## Dependencies and integration points
This depends on the LED class sysfs ABI and on kernels/devices that expose `brightness_hw_changed`. It integrates with the `tools/leds` build as a standalone utility, not as a library.

## Risks and edge cases
`snprintf()` is called with `LED_MAX_NAME_SIZE` even though the destination has extra room for the fixed path prefix, so very long names can be truncated before the suffix is complete. The buffer read is not explicitly NUL-terminated before `atoi()`. Error reporting prints the negative return value from `poll()`/`lseek()` rather than `errno`, limiting diagnostics. The tool assumes sysfs poll semantics are edge-compatible with `POLLPRI`.

## Test signals
Run against an LED device with `brightness_hw_changed`, trigger firmware brightness changes, and verify one timestamp/value line per change. Negative tests should cover missing argument, missing sysfs attribute, long LED names, and CTRL+C cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/led_hw_brightness_mon.c -->
