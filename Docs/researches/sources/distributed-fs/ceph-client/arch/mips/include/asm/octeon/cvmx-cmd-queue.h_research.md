# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-cmd-queue.h

## Purpose
This header provides the common Octeon command queue infrastructure used by hardware blocks such as PKO, ZIP, DFA, RAID, and DMA. It manages chained FPA-backed command buffers, shared queue state in bootmem, fair locking, and optimized inline command writes.

## Important APIs, Types, and Functions
`cvmx_cmd_queue_id_t` encodes unit and queue identifiers, with helpers for PKO and DMA queues. `cvmx_cmd_queue_result_t` reports success, no memory, full, invalid parameter, or already setup. `__cvmx_cmd_queue_state_t` packs queue state: ticket/serving, optional max depth, FPA pool, current buffer pointer, pool size, and current write index. `__cvmx_cmd_queue_all_state_t` stores ticket and state arrays.

Declared APIs initialize/shutdown queues, query length, and return the current command buffer. Inline helpers compute state index, lock/unlock with a ticket-style LL/SC loop, get state, and write one arbitrary command array or fixed two/three-word commands (`cvmx_cmd_queue_write`, `write2`, `write3`).

## Control Flow
Initialization allocates the first FPA command buffer and configures the owning hardware. Writers optionally acquire the queue lock, check max-depth if enabled, append command words to the current buffer when space remains, or allocate a new FPA buffer, link it from the old buffer's final word, advance `base_ptr_div128`, and continue writing. Unlock increments `now_serving` and issues `CVMX_SYNCWS`.

## State and Persistence Behavior
Queue state is global shared memory, typically a named bootmem block called `cvmx_cmd_queues`. Command buffers are FPA blocks linked by physical addresses. Queue state and pending command contents persist until the hardware consumes them or shutdown frees buffers back to FPA. Locks serialize multi-core software producers unless callers disable locking and provide external exclusion.

## Dependencies and Integration Points
It depends on FPA allocation/free, physical/virtual address conversion, Octeon assembly barriers, prefetching, compiler helpers, and hardware-specific wrappers that submit commands and ring doorbells. PKO layout is optimized for per-core/per-port queue locality.

## Risks
This is concurrency- and hardware-facing code. Incorrect index packing, buffer-size assumptions, or lock ordering can corrupt shared queues. FPA exhaustion returns `NO_MEMORY` mid-write before any new buffer can be linked. Disabling locking is only safe for carefully partitioned queues. The packed bitfields assume command buffers are 128-byte aligned and sizes fit the field widths.

## Test Signals
Stress multi-core command producers for PKO/DMA/ZIP users, including buffer-boundary writes, FPA exhaustion, max-depth enabled builds, queue shutdown after hardware stop, and lock fairness under contention. Packet transmission and DMA command completion are end-to-end signals.
