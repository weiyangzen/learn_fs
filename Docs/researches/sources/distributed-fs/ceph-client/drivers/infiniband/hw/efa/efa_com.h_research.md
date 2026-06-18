# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com.h

## Purpose

`efa_com.h` declares the EFA communication-layer data structures and APIs for admin queues, async event queues, MMIO readless register access, event queues, device reset/version/DMA validation, and admin command execution.

## Important APIs, Types, and Functions

- Admin queues: `efa_com_admin_sq`, `efa_com_admin_cq`, `efa_com_admin_queue`, state bits, and `efa_com_stats_admin`.
- Async/event queues: `efa_com_aenq`, `efa_aenq_handlers`, `efa_com_eq`, and callback typedefs.
- Device wrapper: `efa_com_dev` with admin/AENQ state, register BAR, DMA device, supported features, DMA width, and MMIO read state.
- EQ command parameters/results: `efa_com_create_eq_params`, `efa_com_create_eq_result`, and `efa_com_destroy_eq_params`.
- Public APIs: DMA address splitting, admin init/destroy, EQ init/destroy, reset, polling mode, admin/AENQ/EQ interrupt handlers, MMIO read init/destroy, version/DMA validation, and `efa_com_cmd_exec`.

## Control Flow

The header defines the call graph used by probe and verbs command code: initialize MMIO read response storage, validate device versions and DMA width, initialize admin/AENQ queues, execute admin commands, optionally create EQs, handle interrupts, reset on errors, and destroy queues during removal.

## State and Persistence Behavior

Admin queue counters, phase bits, completion contexts, semaphore availability, state bits, and stats persist in `efa_com_dev` for the device lifetime. AENQ and EQ consumer counters/phase persist per queue. MMIO read state serializes register reads with a sequence number and DMA response buffer. These structures are kernel-resident shadows of coherent DMA rings and hardware registers.

## Dependencies and Integration Points

It includes Linux delay/device/DMA/semaphore/scheduler headers, RDMA verbs logging context, common EFA admin and register definitions. It is consumed by `efa_com.c`, `efa_com_cmd.*`, EFA PCI probe/remove, IRQ setup, and verbs object creation paths.

## Risks and Edge Cases

- `EFA_MAX_HANDLERS` fixes AENQ handler table size; firmware event groups beyond 255 require ABI/header changes.
- Queue depths are expected to be powers of two by implementation masks in `efa_com.c`; callers should not pass arbitrary EQ depths.
- `efa_com_admin_queue.dmadev` and `efa_dev` are `void *`, so type safety is deferred to call sites.
- Polling mode state controls both interrupt masking and wait strategy; inconsistent state can cause missed completions or unnecessary polling.

## Test Signals

Build tests should catch API signature drift. Runtime tests should initialize/destroy admin and EQ structures, execute commands through `efa_com_cmd_exec`, toggle polling mode, process AENQ/EQ interrupts, validate callback dispatch, reset the device, and verify stats counters under command success/failure.
