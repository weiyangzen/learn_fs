# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_dev.h

Purpose: Defines Ionic hardware-facing constants, compile-time ABI size checks, device/queue/CQ data structures, queue helper inlines, and low-level device API prototypes.

Important APIs/types/functions: Constants define descriptor limits, watchdog periods, doorbell deadlines, interrupt coalescing defaults, CMB expanded doorbell stride sizes, and XDP MTU bounds. Static asserts lock firmware ABI structure sizes. `struct ionic_dev` holds register pointers, firmware heartbeat state, doorbell/CMB resources, port info DMA memory, and device info strings. `struct ionic_queue` and `struct ionic_cq` describe software/hardware queue rings, SG rings, XDP/page-pool state, CMB mappings, doorbell values, indexes, and completion color. Inlines include `ionic_intr_init()`, `ionic_q_space_avail()`, and `ionic_q_has_space()`.

State and persistence: This header defines the persistent in-memory state manipulated by `ionic_dev.c`, LIF allocation, TX/RX, adminq, debugfs, and ethtool code.

Dependencies and integration: Includes atomic, mutex, workqueue, SKB/BPF trace headers, Ionic firmware ABI, registers, and exported API declarations.

Risks and test signals: ABI size asserts protect firmware command layouts; failures indicate incompatible `ionic_if.h` changes. Queue math assumes power-of-two descriptor counts and one empty slot. Test build with sparse/checker, max/min descriptor counts, XDP MTU boundaries, queue full/empty arithmetic, CMB queue mappings, and PTP disabled/enabled structure users.
