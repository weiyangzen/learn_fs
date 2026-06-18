<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-hammer.c -->
# sources/distributed-fs/ceph-client/tools/gpio/gpio-hammer.c

Purpose: Example tool that repeatedly toggles one or more GPIO output lines and reports their observed states.

Important APIs/types/functions: `hammer_device()` requests selected lines as outputs, initializes a `gpio_v2_line_values` mask, toggles bits with `gpiotools_change_bit()`, writes with `gpiotools_set_values()`, reads back with `gpiotools_get_values()`, and releases the line fd. `main()` parses `-n`, repeated `-o`, optional `-c`, and `-?`.

Control flow: After validation, the tool requests all selected lines together, prints initial states, then sleeps one second per toggle iteration. `loops == 0` means infinite operation.

State and persistence: Runtime state is the held line request fd, values mask/bits, loop counter, and spinner output. There is no persisted configuration.

Dependencies/integration: Depends on GPIO v2 chardev UAPI and `gpio-utils`. It is an interactive/manual exerciser rather than a library.

Risks/tests: Risks include using legacy `GPIOHANDLES_MAX` while v2 APIs use `GPIO_V2_LINES_MAX`, off-by-one reporting for too many `-o` options, and toggling real hardware outputs without safety interlocks. Test signals are loop-limited toggles on dummy GPIO, multiple-line masks, invalid line offsets, and clean release on ioctl failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-hammer.c -->
