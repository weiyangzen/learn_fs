# sources/distributed-fs/ceph-client/arch/mips/kernel/rtlx.c

## Purpose
Implements the RTLX shared-memory ring-buffer channel operations and file operations used for communication between Linux and a service-processor VPE on MIPS MT systems.

## Important APIs, Types, and Functions
- Globals `rtlx`, `channel_wqs`, `rtlx_notify`, and exported `aprp_hook` hold shared state.
- `rtlx_starting()` and `rtlx_stopping()` respond to VPE lifecycle notifications.
- `rtlx_open()` validates and attaches shared RTLX metadata, enforces single opener per channel, and marks channel state opened.
- `rtlx_release()`, `rtlx_read_poll()`, `rtlx_write_poll()`, `rtlx_read()`, and `rtlx_write()` implement channel lifecycle and ring-buffer I/O.
- `rtlx_fops` exposes open/release/read/write/poll/noop_llseek to the char devices.

## Control Flow
Open validates the minor index, increments an atomic open guard, waits for `vpe_get_shared()` and a non-NULL shared pointer when blocking, validates the pointer and RTLX id, initializes `rtlx`, then atomically changes the channel Linux state to opened. Reads poll for data in the Linux-facing ring; blocking reads sleep unless the SP is stopping. Writes poll for free space in the RT-facing ring; blocking writes sleep until space is available. `rtlx_read()` and `rtlx_write()` lock the channel mutex, compute wrapped copy lengths, copy to/from user in up to two segments, update ring indexes with memory barriers, and writes notify the SP through `_interrupt_sp()`.

## State and Persistence
State is shared memory (`struct rtlx_info` and `struct rtlx_channel` indexes/buffers/states), waitqueues/mutexes/open counters, and `sp_stopping`. No disk persistence. Ring indexes are the durable state for in-flight channel data while the SP program is loaded.

## Dependencies and Integration Points
Integrates with VPE loader shared-memory APIs, RTLX IRQ init in `rtlx-mt.c`, Linux character device operations, waitqueue/poll APIs, user copy helpers, and MIPS memory barriers.

## Risks
Shared memory is concurrently accessed by another VPE, so `smp_rmb()`/`smp_wmb()` ordering is important. Ring buffers intentionally keep one byte empty to distinguish full from empty. Blocking open/read/write must handle signals and SP stopping. Invalid shared pointers or RTLX ids must be rejected before dereference. Partial user copies update indexes only for copied bytes.

## Test Signals
Opening the same channel twice should return `-EBUSY`. Nonblocking open without SP should return `-ENOSYS`; blocking open should wake when SP starts. Read/write wraparound should preserve byte order, poll should report readable/writable states, and writes should trigger SP interrupts.
