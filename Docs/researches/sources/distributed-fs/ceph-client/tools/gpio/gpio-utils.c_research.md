<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-utils.c -->
# sources/distributed-fs/ceph-client/tools/gpio/gpio-utils.c

Purpose: Shared helper library for the GPIO tools, wrapping GPIO v2 character-device ioctls for requesting, reading, writing, and releasing lines.

Important APIs/types/functions: `gpiotools_request_line()` opens `/dev/<gpiochip>` and issues `GPIO_V2_GET_LINE_IOCTL`. `gpiotools_set_values()` and `gpiotools_get_values()` wrap line value ioctls. `gpiotools_release_line()` closes a line fd. Convenience APIs `gpiotools_get()`, `gpiotools_gets()`, `gpiotools_set()`, and `gpiotools_sets()` request, operate, and release in one call.

Control flow: Request fills offsets, copies config and consumer, closes the chip fd, and returns the new line fd. Get helpers request input lines, set value masks, read bits, copy results to caller arrays, then release. Set helpers build output-value line attributes, request output lines with initial values, then release immediately.

State and persistence: No persistent state. State exists only in file descriptors and caller-provided `gpio_v2_line_*` structs. Convenience setters do not hold outputs after returning because the line fd is released.

Dependencies/integration: Depends on `/dev/gpiochip*`, `<linux/gpio.h>` v2 ABI, `asprintf`, and helper bit functions from `gpio-utils.h`. Used by `lsgpio`, `gpio-hammer`, and `gpio-event-mon`.

Risks/tests: Risks include unchecked `strcpy()` into `req.consumer`, uninitialized `gpio_v2_line_values` masks if callers fail to zero them, immediate release semantics surprising users of `gpiotools_set()`, and inconsistent legacy ioctl names in error text. Test signals are request/get/set/release against gpio-sim, multi-line masks, invalid consumer lengths, permission failures, and close-error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-utils.c -->
