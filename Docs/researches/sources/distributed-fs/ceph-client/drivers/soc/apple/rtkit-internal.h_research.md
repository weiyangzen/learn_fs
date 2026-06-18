# sources/distributed-fs/ceph-client/drivers/soc/apple/rtkit-internal.h

## Purpose
This private header defines internal Apple RTKit state shared between the protocol implementation and crashlog parser.

## Important APIs, Types, And Functions
It defines endpoint constants and `struct apple_rtkit`, which stores client cookie/ops, device, mailbox, completions, boot result, protocol version, AP/IOP power states, crash flag, endpoint bitmap, shared memory buffers for ioreport/crashlog/oslog/syslog, syslog sizing, and workqueue. It declares `apple_rtkit_crashlog_dump()`.

## Control Flow
The struct fields are used by RTKit boot, endpoint discovery, mailbox RX work dispatch, shared-memory request handling, power-state transitions, and crash notification.

## State, Persistence, And Dependencies
All state is in memory and scoped to an RTKit instance. Dependencies include completions, bitmaps, DMA mapping, workqueues, the public RTKit header, and the Apple mailbox header.

## Integration Points
Only Apple RTKit implementation files should include this header. Client drivers use the public `linux/soc/apple/rtkit.h` APIs instead.

## Risks
This is the central synchronization state for RTKit. Missing locks around some state fields rely on ordered workqueue and lifecycle sequencing. Direct sharing between implementation files means structure changes must be coordinated carefully.

## Test Signals
Compile RTKit and crashlog together, exercise boot/reinit/free, and use concurrency tests around mailbox RX during reinit/shutdown to validate assumptions.
