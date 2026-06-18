# sources/distributed-fs/ceph-client/drivers/misc/hpilo.h

## Purpose
`hpilo.h` defines constants, queue bitfields, and shared structures for the HP iLO driver, including hardware info, channel control blocks, per-file channel data, and FIFO descriptors.

## Important APIs, Types, and Functions
Important types are `struct ilo_hwinfo`, `struct ccb`, `struct ccb_data`, and `struct fifo`. Constants define device limits (`MAX_CCB`, `MIN_CCB`, `MAX_ILO_DEV`, `MAX_OPEN`), wait timing, doorbell offsets, CCB sizes, FIFO queue IDs, control bit positions, descriptor entry bitfields, and conversion macro `FIFOBARTOHANDLE()`.

## Control Flow
The header has no executable flow. Its layouts determine how `hpilo.c` allocates coherent memory, fills software and hardware CCB views, manipulates FIFO head/tail entries, and interprets doorbell reset bits.

## State and Persistence
Structures in this header represent per-device state, per-open channel state, and DMA memory shared with iLO hardware. The FIFO `reset` flag is software-visible state used to force close/reopen after device reset.

## Dependencies and Integration Points
It is private to the `hpilo` driver and relies on PCI, cdev, spinlock, wait queue, DMA address, and I/O memory types included by the C file context.

## Risks and Edge Cases
Hardware ABI depends on exact CCB size and field ordering. Descriptor bitfield macros use integer shifts and masks; invalid lengths or descriptor IDs can corrupt queue state if not bounded by callers. `MAX_ILO_DEV` is one, limiting multi-device support.

## Test Signals
Compile-time structure size/offset checks, FIFO entry encode/decode tests, open limit tests, and hardware queue traces are the main signals that the definitions remain compatible.
