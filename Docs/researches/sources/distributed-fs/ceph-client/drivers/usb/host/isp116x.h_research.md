# sources/distributed-fs/ceph-client/drivers/usb/host/isp116x.h

## Purpose
`isp116x.h` is the private register, bitfield, data-structure, and access-helper header for the ISP116x HCD. It defines host-controller registers, root hub bits, FIFO/PTD format, condition-code error mapping, scheduler constants, controller/endpoint state, register I/O helpers, and optional tracing helpers.

## Important APIs, Types, and Functions
- Register definitions: OHCI-like `HC*` registers, uP interrupt registers, hardware config, DMA config, FIFO ports, buffer status, root hub descriptors/status/port bits.
- Transfer descriptor: packed `struct ptd` plus `PTD_GET_*` and `PTD_*` field macros.
- Status mapping: `cc_to_error[16]` maps PTD condition codes to Linux errno values.
- Runtime structures: `struct isp116x` and `struct isp116x_ep`.
- Access helpers: `isp116x_write_addr()`, `isp116x_write_data16()`, raw 16-bit helpers, 32-bit helpers, `isp116x_read_reg16/32()`, and `isp116x_write_reg16/32()`.

## Control Flow Role
The header underpins all execution in `isp116x-hcd.c`. PTD macros are used before packing FIFO contents and after unpacking hardware results. Register helpers enforce required delays after address/data accesses. Scheduler fields in `struct isp116x` connect async and periodic queue construction to the active FIFO batch.

## State and Persistence Behavior
`struct isp116x` stores controller-wide volatile state: locks, mapped registers, platform data, interrupt masks, cached root hub values, async and periodic schedules, current active FIFO batch, and finishing flag. `struct isp116x_ep` stores per-endpoint volatile state including current PTD, PID, error count, active chain link, periodic placement, and async schedule node.

## Dependencies and Integration Points
The header relies on Linux USB, errno, I/O accessors, debugfs/seq support through users in the C file, and platform delay callbacks controlled by `USE_PLATFORM_DELAY`. It expects platform data to provide timing behavior when platform delays are enabled.

## Risks and Test Signals
Risks include platform delay misconfiguration, endian-sensitive raw vs normal 16-bit FIFO access, packed/aligned PTD assumptions, bitfield macro correctness, and duplicated TD condition-code semantics with the C file. Test signals include compile coverage with/without trace macros and PM/debugfs, sparse/endian checks, PTD encode/decode round trips, register access timing on target hardware, and error-code mapping validation for every PTD condition code.
