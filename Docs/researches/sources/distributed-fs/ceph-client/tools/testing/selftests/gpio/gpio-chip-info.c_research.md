<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-chip-info.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-chip-info.c

## Purpose
This helper reads GPIO chip name, label, or line count from a gpiochip character device.

## Important APIs, Types, And Functions
`main()` opens the provided chip path, calls `GPIO_GET_CHIPINFO_IOCTL` into `struct gpiochip_info`, and prints `name`, `label`, or `num-lines`.

## Control Flow
Invalid argument count or unknown field exits failure. Open or ioctl errors print diagnostics and exit failure.

## State And Persistence
It only opens and reads a GPIO cdev; no persistent state is modified.

## Dependencies And Integration Points
It is used by GPIO shell tests to compare configfs expectations with cdev-visible chip metadata.

## Risks
It opens with `O_RDWR`, which may require write permissions even though it only reads metadata.

## Test Signals
Expected output is one line containing the requested chip field and exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-chip-info.c -->
