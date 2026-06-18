# File Research: sources/block-storage/util-linux/libblkid/src/topology/ioctl.c

## Scope

Provides generic Linux block topology probing through ioctls.

## Behavior

- Reads alignment offset, minimum I/O size, optimal I/O size, physical block size, and disk sequence number.
- Exports values through topology setter APIs.
- Fails the probe if any required ioctl in the sequence is unavailable.

## Dependencies And Risks

- Requires a block-device fd supporting modern topology ioctls.
- Since all ioctls are chained, partial availability does not produce a successful result from this driver.
