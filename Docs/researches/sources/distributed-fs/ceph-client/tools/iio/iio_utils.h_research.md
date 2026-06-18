# sources/distributed-fs/ceph-client/tools/iio/iio_utils.h

## Purpose

`iio_utils.h` declares the shared helper interface and channel metadata structure used by the IIO example tools.

## Important APIs and Types

The header defines `IIO_MAX_NAME_LENGTH`, format strings for buffer and event sysfs directories, `ARRAY_SIZE`, and external `iio_dir`. `struct iio_channel_info` captures channel name, generic name, scale, offset, index, storage bytes, used bits, shift, mask, endian flag, signed flag, and computed scan location. Inline `iioutils_check_suffix` tests suffixes safely. Function prototypes cover channel-name parsing, float parameter lookup, channel array building and sorting, device/trigger lookup, and integer/string/float sysfs access.

## State, Dependencies, and Integration

The header itself has no state; it defines ownership expectations for allocated channel arrays and strings returned by `iio_utils.c`. It depends on `<stdint.h>` and on consumers including standard string declarations before using the inline function, as the header calls `strlen` and `strncmp`.

## Risks and Test Signals

Changes to `struct iio_channel_info` affect every IIO tool's scan parsing and cleanup loops. Format constants must match actual sysfs layout. Tests should compile all IIO tools with warnings enabled and run channel-array construction on devices with multiple channels, mixed endianness, and scale/offset attributes.
