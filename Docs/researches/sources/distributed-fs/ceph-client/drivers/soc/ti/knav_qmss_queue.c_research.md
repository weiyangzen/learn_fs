# sources/distributed-fs/ceph-client/drivers/soc/ti/knav_qmss_queue.c

## Purpose
This file implements the TI Keystone Queue Manager Subsystem. It creates hardware queues, descriptor regions, descriptor pools, PDSP firmware support, queue range discovery, queue notification, and exported queue/pool APIs used by networking and DMA clients.

## Important APIs, Types, And Functions
Exported APIs include `knav_qmss_device_ready`, `knav_queue_notify`, `knav_queue_open`, `knav_queue_close`, `knav_queue_device_control`, `knav_queue_push`, `knav_queue_pop`, `knav_pool_create`, `knav_pool_destroy`, descriptor virt/DMA conversion, descriptor map/unmap, `knav_pool_desc_get`, `knav_pool_desc_put`, and `knav_pool_count`. Probe helpers cover qmgr mapping, PDSP init/load/start/stop, link RAM, descriptor regions, queue ranges, queue instances, and debugfs.

## Control Flow
Probe allocates singleton `kdev`, enables runtime PM, reads global queue range, initializes queue managers, optionally loads PDSP accumulator firmware, parses queue pools/ranges, configures link RAM, allocates descriptor regions, initializes queue instances, creates debugfs, and marks ready. Queue open selects by type or explicit ID, enforces reserved/shared/exclusive rules under `knav_dev_lock`, creates a handle, sets register windows, and opens range-specific IRQ/accumulator resources for first user. Push writes a packed descriptor pointer/size to the push register. Pop either drains the accumulator software ring or reads the hardware pop register. Pools allocate slices from descriptor regions and back them with a general-purpose queue.

## State And Persistence
Global state includes singleton `kdev`, `device_ready`, queue/region/pool/PDSP/qmgr lists, per-instance handle lists, notifier counts, per-handle percpu stats, descriptor region memory, link RAM, PDSP loaded/started flags, and debugfs output. Hardware state includes queue threshold/pop/push registers, link RAM registers, descriptor region registers, and PDSP IRAM/command/intd state.

## Dependencies And Integration Points
It depends on device-tree children `qmgrs`, `pdsps`, `queue-pools`, `descriptor-regions`, `linkram0`, optional `linkram1`, IRQ specs, and firmware `ks2_qmss_pdsp_acc48.bin`. It integrates with `knav_qmss_acc.c`, runtime PM, debugfs, DMA APIs, and public Keystone QMSS clients.

## Risks And Test Signals
Risks include singleton design, TODO-level remove cleanup, firmware absence disabling accumulator ranges, descriptor-pool fragmentation, IRQ affinity failure leaks, busy queue sharing mistakes, link RAM misconfiguration, and DMA address truncation to 32 bits. Test signals include successful probe logs for qmgrs/regions/PDSPs, debugfs `qmss`, descriptor pool create/destroy, queue push/pop count consistency, accumulator and QPEND notifications, and runtime PM enable/disable behavior.
