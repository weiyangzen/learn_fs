# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/nic_common.h

## Purpose

`nic_common.h` provides architecture-neutral inline wrappers and declarations for common NIC operations. It bridges high-level driver code to `efx->type` callbacks for TX, RX, event queues, interrupts, buffers, register dumps, and stats while also defining revision IDs and low-level descriptor/event helpers.

## Important APIs, Types, and Functions

Revision constants include `EFX_REV_SIENA_A0`, `EFX_REV_HUNT_A0`, and `EFX_REV_EF100`; `efx_nic_rev()` returns `efx->type->revision`. Descriptor/event helpers include `efx_event()`, `efx_event_present()`, `efx_tx_desc()`, `efx_rx_desc()`, `efx_nic_tx_is_empty()`, and `efx_nic_may_push_tx_desc()`.

Wrapper groups dispatch to NIC type callbacks: `efx_nic_probe_tx()`, `efx_nic_init_tx()`, `efx_nic_remove_tx()`, `efx_nic_push_buffers()`, `efx_nic_probe_rx()`, `efx_nic_init_rx()`, `efx_nic_remove_rx()`, `efx_nic_notify_rx_desc()`, `efx_nic_generate_fill_event()`, `efx_nic_probe_eventq()`, `efx_nic_init_eventq()`, `efx_nic_fini_eventq()`, `efx_nic_remove_eventq()`, `efx_nic_process_eventq()`, and `efx_nic_eventq_read_ack()`.

It also declares interrupt lifecycle, coherent buffer helpers, register dump functions, stats helpers, and `EFX_MAX_FLUSH_TIME`.

## Control Flow

Common code uses this header instead of calling hardware implementations directly. Queue probe/init/remove/write and event queue operations become a single inline callback dispatch, allowing farch, EF10-like, or future hardware types to share upper-layer code. The TX push helper encodes a Siena/Falcon hardware-bug-aware rule: only push one descriptor when the completion path's empty marker suggests the NIC saw the queue empty.

## State and Persistence Behavior

Inline helpers read and write queue counters such as `empty_read_count`, descriptor ring buffers, event queue buffers, and event read pointers. They do not allocate resources directly except through callback dispatch. `efx_update_diff_stat()` enforces monotonic synthetic counters by only storing positive deltas.

## Dependencies, Risks, and Test Signals

The event-present helper intentionally checks both dwords for all-ones because DMA may not atomically write a full 64-bit event. Any optimization here risks event reordering bugs. The TX empty/push logic depends on producer/consumer counters and hardware errata. Tests should include event queue processing under DMA stress, TX completion/push paths, descriptor ring wraparound, all NIC type callback tables, interrupt self-tests, stats monotonicity, and flush timeout handling.
