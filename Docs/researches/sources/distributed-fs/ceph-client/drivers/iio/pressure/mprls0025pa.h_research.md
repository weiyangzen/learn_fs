<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa.h -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa.h

## Purpose
`mprls0025pa.h` is the private contract shared by the Honeywell MPR common core and its I2C/SPI wrappers. It defines command constants, the runtime data structure, bus operations, and the exported common probe.

## Important APIs, types, and functions
Constants define measurement frame size and NOP/SYNC command packet lengths. `enum mpr_func_id` names transfer functions A, B, and C. `struct mpr_data` holds device pointers, ops, pressure configuration, scale/offset, reset GPIO, IRQ completion, scan buffer, and DMA-aligned RX/TX buffers. `struct mpr_ops` supplies bus read/write callbacks. `mpr_common_probe()` is the shared registration entry point.

## Control flow
There is no executable flow in the header. Bus wrappers fill `struct mpr_ops` and call `mpr_common_probe()`, while the core uses the fields defined here for locking, conversion, and IIO buffering.

## State and persistence behavior
The header describes per-device state but stores none. The DMA alignment annotation on `rx_buf` is part of the transport safety contract.

## Dependencies and integration points
It depends on kernel completion, mutex, IIO, and type definitions. It is internal to the MPR driver family and imported by both bus wrappers.

## Risks
Changing packet lengths, command values, or buffer sizes affects both transports. `struct mpr_data` exposes many core internals to wrappers, so wrappers can accidentally rely on layout details.

## Test signals
Compile both transport modules with the core, validate namespace exports, and run static checks for DMA alignment and buffer-size assumptions in I2C/SPI callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa.h -->
