# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/main.c

Purpose: core MHI endpoint bus stack. It registers endpoint controllers, exposes the `mhi_ep` bus, creates/destroys endpoint client devices on channel start/reset, processes host command/channel doorbells, handles MHI state transitions and resets, and provides data-transfer APIs to endpoint client drivers.

Important APIs: exported `mhi_ep_register_controller()`, `mhi_ep_unregister_controller()`, `mhi_ep_power_up()`, `mhi_ep_power_down()`, `mhi_ep_queue_skb()`, `mhi_ep_queue_is_empty()`, `__mhi_ep_driver_register()`, and `mhi_ep_driver_unregister()`. Internal workers process command rings, channel rings, state transitions, and reset recovery.

Control flow: controller registration validates transport callbacks, initializes channels/caches/workqueue/IRQ, writes MHI version/environment, allocates controller device, and registers it on the bus. Power-up masks interrupts, resets MMIO, initializes rings, enters READY, waits for host M0, maps host contexts, starts command ring, enables interrupts, and enables IRQ. IRQ handling acknowledges control interrupts, schedules reset on host reset, queues state work for M0/M3, queues command ring work on CRDB, and queues channel ring work from channel DB masks.

Transfer behavior: START_CHAN starts a channel ring, sets state RUNNING, sends command completion, creates paired UL/DL client devices on even UL channels, and enables channel DB. UL doorbells trigger async reads from host TRE buffers with callbacks and EOB/EOT events. DL sends use `mhi_ep_queue_skb()` to write skb data into host TREs and send OVERFLOW or EOT completions. STOP/RESET notify clients with `-ENOTCONN`, update channel state, and reset rings.

State and persistence: state spans controller IDA index, controller device, channel array, command/event rings, kmem caches, workqueue, lists, per-channel locks, `enabled`, MHI state, cached host contexts, and dynamic client devices. Reset/power-down tears down transfers, devices, rings, host mappings, interrupts, and event arrays.

Dependencies and integration: depends on endpoint MMIO/ring/state helpers, controller transport callbacks (`read_sync`, `write_sync`, `read_async`, `write_async`, `alloc_map`, `unmap_free`, `raise_irq`), Linux device/bus model, IRQ/workqueue APIs, skbuffs, and public MHI endpoint driver APIs.

Risks: concurrency is complex across IRQ, workqueue, channel locks, event lock, state lock, and async completion callbacks. Dynamic device lifetime relies on paired channel names and reference counts. Partial TD handling is explicitly TODO for DL. Reset recovery only re-powers after SYS_ERR. Test signals include controller register/unregister, power-up/down, M0/M3 transitions, host reset, START/STOP/RESET command completions, paired device probe/remove, UL/DL transfers including chained TREs and overflow, interrupt moderation, and client-driver callback disconnect paths.
