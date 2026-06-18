<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-line-name.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-line-name.c

## Purpose
This helper reads a GPIO v2 line name for a specified chip path and offset.

## Important APIs, Types, And Functions
`main()` parses the offset with `strtoul()`, fills `struct gpio_v2_line_info`, calls `GPIO_V2_GET_LINEINFO_IOCTL`, and prints `info.name`.

## Control Flow
Invalid arguments, nonnumeric offsets, open failure, or ioctl failure produce usage/error and nonzero exit.

## State And Persistence
It reads GPIO line metadata only.

## Dependencies And Integration Points
It is used by `gpio-sim.sh` and `gpio-aggregator.sh` to verify line names visible through the cdev ABI.

## Risks
It relies on GPIO cdev v2 support; kernels with only v1 cdev cannot satisfy it.

## Test Signals
Expected output is the line name, including an empty line when the name is unset, with exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-line-name.c -->
