# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pio.h

## Purpose
`pio.h` defines the public structures, constants, and function contracts for HFI1 PIO send-context management and PIO memory copy support.

## Important APIs, Types, And Functions
The header defines send-context type IDs (`SC_KERNEL`, `SC_VL15`, `SC_ACK`, `SC_USER`), PIO release reason bits, `union mix`, `struct pio_buf`, `union pio_shadow_ring`, `struct send_context`, `struct send_context_info`, credit-return DMA structures, context sizing structures, and the RCU VL map types `pio_map_elem` and `pio_vl_map`. It declares lifecycle APIs such as `init_sc_pools_and_sizes()`, `init_send_contexts()`, `sc_alloc()`, `sc_enable()`, `sc_disable()`, `sc_restart()`, `sc_buffer_alloc()`, `sc_release_update()`, `pio_map_init()`, and the segmented/non-segmented copy routines.

## Control Flow
The declarations describe the normal PIO path: initialize credit-return and send contexts, allocate/enable contexts, publish VL mappings, select a context, allocate a `pio_buf`, copy packet bytes, and release/wake based on credit returns. The struct layout separates read-mostly initialization fields, allocation fields, release fields, wait-list state, and credit-control state into cacheline-conscious groups.

## State And Persistence
`struct send_context` is the main in-memory persistent runtime state for a hardware context. It retains CSR identity, PIO base address, credit counters, shadow-ring state, per-CPU outstanding allocation counters, interrupt enable counts, wait queue/list state, and halt work until freed. `struct pio_buf` tracks one allocated PIO buffer and carries partial bytes for segmented copies.

## Dependencies And Integration Points
The header ties together HFI1 device data, QP waiters, DMA credit-return memory, Linux RCU/list/waitqueue/workqueue primitives, PIO copy code, and diagnostic seqfile dumping. It is included by send paths, QP code, user context code, and low-level PIO implementation.

## Risks
Several fields are intentionally touched from different locks or interrupt contexts, so changing struct layout or semantics can introduce cacheline contention or races. `pio_release_cb` codes are bit flags and callback users must tolerate combined reasons. `SC_USER` being the last type is a configuration assumption. The RCU map uses flexible arrays and rounded power-of-two masks, which requires allocation and bounds discipline.

## Test Signals
Compile tests should catch prototype drift. Runtime coverage should validate context selection, callback reason handling, segmented-copy state in `pio_buf`, credit interrupt refcounting, and RCU map replacement/freeing with concurrent readers.
