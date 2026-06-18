# sources/distributed-fs/ceph-client/drivers/net/wan/fsl_qmc_hdlc.c

Purpose: Freescale/NXP QMC HDLC netdevice driver. It binds a QMC channel to the Linux generic HDLC stack, optionally controls an external framer, maps TE1 timeslots, queues DMA-backed RX/TX descriptors, and reports carrier based on framer status.

Important APIs, types, and functions: state is held in `struct qmc_hdlc` and descriptor metadata in `struct qmc_hdlc_desc`. Framer helpers are `qmc_hdlc_framer_init()`, `qmc_hdlc_framer_start()`, `qmc_hdlc_framer_stop()`, `qmc_hdlc_framer_set_iface()`, `qmc_hdlc_framer_get_iface()`, and the notifier callback. Data path helpers include `qmc_hdlc_recv_queue()`, `qmc_hcld_recv_complete()`, `qmc_hdlc_xmit_queue()`, `qmc_hdlc_xmit_complete()`, and `qmc_hdlc_xmit()`. Interface and timeslot management uses `qmc_hdlc_xlate_slot_map()`, `qmc_hdlc_xlate_ts_info()`, `qmc_hdlc_set_iface()`, and `qmc_hdlc_ioctl()`.

Control flow: probe obtains a child QMC channel, verifies it is in HDLC mode, reads current timeslot masks into `slot_map`, optionally gets and initializes a framer, allocates/registers an HDLC netdev, and installs HDLC attach/xmit ops. Open powers on the framer, registers carrier notifier, opens HDLC, configures QMC HDLC parameters, queues RX descriptors, starts the channel, and starts the netdev queue. RX completion unmaps DMA, handles QMC error flags, strips CRC, submits the SKB, and requeues the descriptor. TX maps the SKB, submits it to QMC, advances the ring, and wakes the queue on completion.

State and persistence: state is in memory and QMC/framer hardware. TX descriptors hold SKBs until completion. RX descriptors are continuously recycled. `slot_map` caches the user-visible compact timeslot map. `is_crc32` is selected by HDLC attach parity. There is no persistent storage.

Dependencies and integration points: depends on `soc/fsl/qe/qmc.h`, DMA mapping, generic HDLC, TE1 WAN ioctls, generic framer APIs, notifier chains, mutex/spinlock helpers, and platform/OF matching for `fsl,qmc-hdlc`.

Risks: RX requeue failure after completion leaves fewer active descriptors and only increments errors. Timeslot translation assumes TX/RX availability masks match and that compact slot maps fit 32 bits. Framer set-interface can fail after QMC timeslots were already changed, leaving partial configuration. TX queue capacity depends on callbacks freeing descriptors; missing completions stop progress.

Test signals: probe with and without optional framer, QMC mode mismatch, timeslot translation round trips, E1/T1 ioctl get/set while down, open/close cleanup after partial RX queueing, CRC16 and CRC32 attach modes, RX error counters for overflow/unaligned/CRC/abort flags, TX descriptor exhaustion/wakeup, carrier notifier behavior, and DMA mapping failure paths.
