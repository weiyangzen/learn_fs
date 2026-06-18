# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sdma.h

## Purpose
`sdma.h` defines the public and internal-facing contract for HFI1 send DMA. It provides descriptor format constants, SDMA state/event enums, core `struct sdma_engine` layout, VL mapping structures, tx request initialization and descriptor-building helpers, engine selection APIs, progress helpers, lifecycle APIs, AHG helpers, and debug/sysfs support declarations.

## Important APIs, Types, and Functions
- Descriptor constants define hardware descriptor fields for physical address, byte count, first/last flags, header update mode, AHG header index, generation bits, interrupt request, and head-to-host update.
- `enum sdma_states` and `enum sdma_events` enumerate the state machine implemented in `sdma.c`.
- `struct sdma_state` stores state-machine reference count, completion, current and previous state/op, running intent, and last event.
- `struct hw_sdma_desc` is the raw 128-bit ring descriptor.
- `struct sdma_engine` stores device/port links, CSR addresses, interrupt masks, coherent head and descriptor memory, tx ring, state machine, locks, head/tail indices, wait/flush lists, tasklets/workers/timers, AHG bitmap, CPU affinity mask, and sysfs kobject.
- `sdma_txinit()` and `sdma_txinit_ahg()` initialize `struct sdma_txreq` instances and optionally encode AHG copy/update metadata.
- `sdma_txadd_page()`, `sdma_txadd_kvaddr()`, and `sdma_txadd_daddr()` append DMA descriptors and close/pad a packet when the expected length is satisfied.
- `sdma_send_txreq()` and `sdma_send_txlist()` are submission APIs implemented in `sdma.c`.
- `sdma_select_engine_sc()`, `sdma_select_engine_vl()`, and `sdma_select_user_engine()` pick engines from SC/VL and user affinity maps.
- `sdma_progress()` lets iowait code detect whether descriptor progress occurred since a saved sequence.

## Control Flow
Callers allocate an enclosing object with `struct sdma_txreq` first, initialize it with `sdma_txinit()` or `sdma_txinit_ahg()`, add fragments using one of the `sdma_txadd_*()` helpers until `tx->tlen` reaches zero, and submit through `sdma_send_txreq()` or `sdma_send_txlist()`. The add helpers map pages or kernel virtual addresses for DMA, record mapping type and optional pinning context in each `sdma_desc`, decrement `tlen`, and mark the last descriptor when the packet is complete. If the built-in descriptor array is exhausted, `sdma.c` extends or coalesces descriptors.

Engine selection and lifecycle are declared here but implemented in `sdma.c`. Consumers use `sdma_running()` or submit APIs rather than directly changing engine state. Interrupt handlers call `sdma_engine_interrupt()` or `sdma_engine_error()`. Debug and sysfs code calls dump and mapping helpers.

## State and Persistence Behavior
The header describes in-memory runtime state only. `sdma_txreq` owns temporary descriptor arrays, DMA mappings, optional coalesce buffer, wait pointer, callback, AHG flags, and packet length counters until completion or cleanup. `sdma_engine` owns coherent DMA rings and state-machine data for the device lifetime. No state is persisted across module unload or device reset.

## Dependencies and Integration Points
`sdma.h` includes HFI1 core headers, verbs declarations, Linux list/workqueue/RCU types, and `sdma_txreq.h`. It is included by SDMA implementation and by packet producers in verbs, user SDMA, IPOIB, pinning, QP selection, sysfs, and RC/RUC code for AHG integration. The inline helpers depend on DMA mapping APIs and HFI1 device memory such as `dd->sdma_pad_phys` and `dd->default_desc1`.

## Risks and Edge Cases
The inline API assumes `tlen` is exact and all fragments sum to the initialized packet length. Calling submit with nonzero `tlen` is invalid. `sdma_txadd_daddr()` assumes the caller owns DMA mapping lifetime; `sdma_txadd_page()` and `sdma_txadd_kvaddr()` transfer unmap responsibility to SDMA cleanup. Last-descriptor padding uses a coherent pad buffer. AHG mode values are coupled to skip-count logic in `sdma.c`, so enum-like macro values must not change casually. `sdma_descq_freecnt()` relies on power-of-two descriptor counts and wrap semantics.

## Test Signals
Compile coverage is important because many helpers are inline. Runtime tests should build packets from page, kvaddr, and caller-DMA fragments; exercise exact-length, zero-length, oversize, and non-dword-sized packets; test AHG copy and update modes; force descriptor extension and coalescing; and validate cleanup after mapping failure. Engine selection tests should cover SC/VL maps and user CPU affinity.
