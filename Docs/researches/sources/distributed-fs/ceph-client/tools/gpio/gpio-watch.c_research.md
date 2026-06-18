<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-watch.c -->
# sources/distributed-fs/ceph-client/tools/gpio/gpio-watch.c

Purpose: Watches unrequested GPIO lines for line-info changes such as request, release, or configuration changes.

Important APIs/types/functions: `main()` opens a gpiochip path supplied as argv[1], issues `GPIO_V2_GET_LINEINFO_WATCH_IOCTL` for each supplied line offset, then polls the chip fd and reads `struct gpio_v2_line_info_changed` events.

Control flow: After registering watches, the process loops forever with a 5-second poll timeout. When an event arrives it maps event type to text and prints line offset, event name, and timestamp.

State and persistence: Runtime state is the chip fd and kernel watch registrations associated with it. No persistent state is written.

Dependencies/integration: Depends on GPIO v2 line-info watch ABI and poll/read on the gpiochip character device. Unlike the other GPIO tools, it does not use `gpio-utils`.

Risks/tests: Risks include no way to unregister except process exit, infinite loop without signal cleanup needs, sparse argument validation, and failure if lines are requested before watch setup. Test signals are watching a gpio-sim chip while another process requests/releases/configures lines, invalid offset parsing, and read-size error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-watch.c -->
