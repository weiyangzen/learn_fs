# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/ultrasoc-smb.h

## Purpose

`ultrasoc-smb.h` defines the register offsets, bit fields, default register values, resource indices, and driver data structures for the UltraSoc/Siemens SMB CoreSight sink.

## Important APIs, Types, and Functions

The header maps global config/enable/interrupt registers, logical buffer config/status/read/write/purge registers, default configuration values, interrupt bits, resource indices, and buffer base masks. `struct smb_data_buffer` stores mapped buffer address, hardware base, size, available data, and read pointer. `struct smb_drv_data` stores MMIO base, CoreSight device, buffer state, miscdevice, lock, reading flag, and owner pid.

## Control Flow

The C file uses these constants to initialize SMB hardware, detect non-empty/full state, update read pointers, reset/purge buffers, expose management registers, and map platform resources.

## State and Persistence Behavior

The structures define persistent device state. `buf_rdptr` and `data_size` are mutable software mirrors of hardware circular-buffer state; `pid` and `reading` serialize ownership between perf and miscdevice users.

## Dependencies and Integration Points

It depends on bitfield helpers, miscdevice, and spinlock definitions. It is private to `ultrasoc-smb.c` and its CoreSight sink integration.

## Risks and Edge Cases

Default bitfield values must match hardware expectations. The low 32-bit hardware base mask encodes an architectural limitation that may not work for buffers above 4 GiB. Software and hardware read pointers must remain synchronized.

## Test Signals

Validate register default encodings, resource index use, buffer size/resource parsing, read/write pointer arithmetic, purge/reset status bits, and owner-state transitions.
