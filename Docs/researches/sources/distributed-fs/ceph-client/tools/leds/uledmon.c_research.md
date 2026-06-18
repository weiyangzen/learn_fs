<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/uledmon.c -->
# sources/distributed-fs/ceph-client/tools/leds/uledmon.c

## Purpose
`uledmon.c` creates a userspace LED class device through `/dev/uleds` and monitors brightness changes requested by the LED subsystem. It is a simple exerciser for the uleds interface: userspace registers the LED, then blocks reading brightness updates.

## Important APIs, types, and functions
The `main()` function fills `struct uleds_user_dev` with a user-provided `name` and `max_brightness = 100`, opens `/dev/uleds` read-write, writes the registration structure, then repeatedly reads an `int brightness` and prints it with a `CLOCK_MONOTONIC` timestamp. It relies on `LED_MAX_NAME_SIZE` and the uleds character device ABI from `<linux/uleds.h>`.

## Control flow
After argument validation, the program registers the uleds device by writing the full `struct uleds_user_dev`. A successful write transitions into an endless blocking `read()` loop. A read failure prints `perror()`, closes the fd, and exits nonzero.

## State and persistence behavior
No state persists after process exit. The lifetime of the LED class device is tied to the open `/dev/uleds` file descriptor. Runtime state is the registration struct, fd, last brightness value, and timestamp.

## Dependencies and integration points
The tool requires a kernel with the uleds driver and permissions to open `/dev/uleds`. The created LED appears under the kernel LED class, so other LED sysfs tooling can drive brightness changes that this process observes.

## Risks and edge cases
`struct uleds_user_dev uleds_dev` is not zero-initialized before `strncpy()`, so names of length `LED_MAX_NAME_SIZE` may lack a terminator and padding bytes can contain stack data. The write only checks `ret == -1`; a short write would be treated as success. The printed brightness uses `%u` for an `int`. The infinite loop has no graceful cleanup beyond process termination.

## Test signals
Build and run with a unique device name, confirm a new `/sys/class/leds/<name>` appears, write different brightness values through sysfs, and verify matching timestamp/value output. Tests should also cover missing `/dev/uleds`, permissions, and maximum-length names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/uledmon.c -->
