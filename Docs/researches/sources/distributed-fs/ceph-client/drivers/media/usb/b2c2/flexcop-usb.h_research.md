# sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/flexcop-usb.h

## Purpose
Defines the B2C2 FlexCop USB private state, USB pipe macros, vendor request IDs, I2C utility function IDs, V8 memory constants, and transfer sizing.

## Important APIs, types, and functions
Transfer constants are four ISO frames per URB and four ISO URBs. `struct flexcop_usb` stores USB device/interface, coherent ISO buffer/DMA address, ISO URBs, owning `flexcop_device`, partial TS frame buffer, control-transfer scratch data, and a mutex protecting that data. Request enums cover register, V8 memory, flash, I2C, and utility operations. Utility enums cover data/filter/buffer/SRAM operations. V8 memory constants define pages, extended bit, max read/write/flash chunk sizes, and 32 KiB page mask.

## Control flow and state
No executable flow. The struct describes persistent USB transport state allocated as the bus-specific portion of `struct flexcop_device`. Pipe macros depend on a local `fc_usb` variable and are used in control and ISO setup code.

## Dependencies and integration points
Includes USB core and forward-integrates with common FlexCop code through the `fc_dev` pointer. Request constants are the ABI used by firmware in `flexcop-usb.c`.

## Risks and test signals
Risks include macro dependence on variable names, scratch buffer size limits for control transfers, partial-frame buffer sizing, and request enum drift from firmware. Test signals are no oversized control requests, successful V8 flash/MAC reads, and stable ISO transfer setup.
