<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/defs.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/defs.h

Purpose: Provides small common GPIO direction constants shared by GPIO headers.

Important APIs/types/functions: Defines `GPIO_LINE_DIRECTION_IN` as `1` and `GPIO_LINE_DIRECTION_OUT` as `0`.

Control flow: Consumers compare or assign direction values using these constants.

State and persistence behavior: No state; compile-time constants only.

Dependencies and integration points: Included by `gpio/consumer.h` and any code needing direction constants without the full GPIO API.

Risks: Direction values are intentionally simple but must stay aligned with gpiolib expectations and UAPI-adjacent representations.

Test signals: Compile coverage and GPIO direction tests that map descriptor direction queries to these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/defs.h -->
