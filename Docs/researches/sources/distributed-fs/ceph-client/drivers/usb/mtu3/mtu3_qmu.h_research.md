# Research: sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_qmu.h

Purpose: declares the MTU3 QMU interface used by the gadget endpoint code and defines descriptor-ring sizing and maximum buffer constants. It is the narrow public contract for allocating QMU rings, preparing descriptors, controlling hardware queues, and servicing QMU interrupts.

Important APIs, types, and symbols: constants are `MAX_GPD_NUM`, `QMU_GPD_SIZE`, `QMU_GPD_RING_SIZE`, `GPD_BUF_SIZE`, and `GPD_BUF_SIZE_EL`. Function declarations cover queue control (`mtu3_qmu_start`, `mtu3_qmu_stop`, `mtu3_qmu_resume`, `mtu3_qmu_flush`), descriptor insertion and capacity checks (`mtu3_insert_gpd`, `mtu3_prepare_transfer`), ring lifetime (`mtu3_gpd_ring_alloc`, `mtu3_gpd_ring_free`), interrupt handling (`mtu3_qmu_isr`), and global pool lifetime (`mtu3_qmu_init`, `mtu3_qmu_exit`).

Control flow: the header encodes the lifecycle expected by users: initialize the controller QMU pool once, allocate a ring per endpoint, prepare/insert GPDs as requests are queued, start/resume/stop/flush the endpoint queue as endpoint state changes, handle QMU interrupts through `mtu3_qmu_isr`, free endpoint rings, and finally destroy the controller pool.

State and persistence: no persistent state is declared. The constants define in-memory DMA ring shape: 64 descriptors per endpoint and one contiguous ring sized as `MAX_GPD_NUM * sizeof(struct qmu_gpd)`. Buffer limits distinguish original hardware with roughly 64 KiB GPD data length from extended layout hardware with roughly 1 MiB descriptors.

Dependencies and integration points: assumes `struct mtu3`, `struct mtu3_ep`, `struct mtu3_request`, `struct qmu_gpd`, and `irqreturn_t` are visible through the including MTU3 driver headers. It is consumed by MTU3 gadget and core files that need QMU acceleration but keeps descriptor bit layout private to `mtu3_qmu.c`.

Risks: `QMU_GPD_SIZE` depends on the included definition of `struct qmu_gpd`; compile-time ordering matters. The buffer-size constants are not enforced in this header, so callers and descriptor-preparation code must ensure request segmentation or rejection. `mtu3_prepare_transfer` has a misleading name because its implementation returns the ring-full condition rather than preparing hardware directly.

Test signals: compile all MTU3 files that include this header, check `QMU_GPD_SIZE == 16` at runtime build assertion in `mtu3_qmu.c`, and exercise queueing limits around 64 descriptors plus old/new hardware maximum request lengths.
