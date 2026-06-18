<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-event-mon.c -->
# sources/distributed-fs/ceph-client/tools/gpio/gpio-event-mon.c

Purpose: Monitors GPIO line edge events from userspace using the GPIO v2 character-device API.

Important APIs/types/functions: `monitor_device()` requests one or more input lines with event flags, reads initial values, then reads `struct gpio_v2_line_event` records. `main()` parses `-n`, repeated `-o`, `-r`, `-f`, `-d`, `-s`, `-w`, `-t`, `-b`, and `-c`. `EDGE_FLAGS` defaults to both rising and falling edges.

Control flow: CLI parsing fills a `gpio_v2_line_config`; debounce is added as a line attribute over all selected lines. `monitor_device()` opens `/dev/<gpiochip>`, requests the event line fd through `gpiotools_request_line()`, prints initial values, then blocks reading events until the optional loop count is reached or an error occurs.

State and persistence: Holds chip and line fds during monitoring; no persistent state. Event output is printed to stdout with timestamp, offset, line sequence, global sequence, and edge type.

Dependencies/integration: Depends on `<linux/gpio.h>` v2 ioctls and shared `gpio-utils` helpers. Integrates with GPIO chardev event facilities and optional hardware timestamp engine clock selection.

Risks/tests: Risks include an ineffective `errno == -EAGAIN` check, missing nonblocking setup despite mentioning no data, line-count bounds, debounce attribute mask mistakes, and open drain/source combinations on input lines. Test signals are rising/falling event generation, multiple lines, debounce, realtime/HTE timestamps, loop termination, and invalid chip/offset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-event-mon.c -->
