# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio-service.c

Purpose: exported DPAA2 IO service layer built on QBMan software portals. It selects per-CPU or round-robin DPIO services and exposes notification, enqueue, dequeue, buffer pool, query, and IRQ coalescing APIs to DPAA2 object drivers.

Important APIs and functions: creation/destruction through `dpaa2_io_create()` and `dpaa2_io_down()`. Selection through `dpaa2_io_service_select()`. IRQ dispatch through `dpaa2_io_irq()`. Notification APIs include `dpaa2_io_service_register()`, `dpaa2_io_service_deregister()`, and `dpaa2_io_service_rearm()`. Data APIs include pull, enqueue single/multiple, release/acquire, store create/destroy/next, FQ/BP count queries, IRQ coalescing, adaptive coalescing, and Net DIM update functions.

Control flow: DPIO creation initializes a `qbman_swp`, enables DQRR interrupts and optional push dequeue, inserts the object into global list/per-CPU array, and initializes DIM state. Service calls select a portal, build a QBMan descriptor, and call the relevant `qbman_swp_*` primitive. IRQ handling reads portal status, drains up to `DPAA_POLL_MAX` DQRR entries, invokes notification callbacks for SCNs, consumes entries, clears status, and uninhibits interrupts.

State and persistence: global `dpio_by_cpu[]`, `dpio_list`, and `dpio_list_lock` manage service selection. Each `dpaa2_io` owns a `qbman_swp`, notification list, management-command lock, notification lock, DIM counters, and device pointer. `dpaa2_io_store` owns DMA-mapped dequeue result memory.

Dependencies and integration: integrates with `soc/fsl/dpaa2-io.h`, MC DPIO driver, QBMan portal implementation, DMA mapping, device links, and networking DIMLIB.

Risks and test signals: risks include concurrency around round-robin service selection, missing `qbman_swp_finish()` in teardown, caller misuse of store polling, descriptor allocation fixed at 32 entries in multi-desc enqueue, and callbacks running in IRQ context. Test signals are DPAA2 Ethernet traffic, notification rearm correctness, DMA mapping checks, IRQ coalescing ethtool behavior, and stress with CPU affinity and hotplug.
