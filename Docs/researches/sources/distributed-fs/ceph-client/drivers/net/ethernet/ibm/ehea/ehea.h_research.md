# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea.h

Purpose: Central private header for the IBM eHEA driver. It defines driver identity, queue sizing, adapter/port/resource structures, bitfield helpers, memory-region busmap structures, multicast bookkeeping, kdump handle tracking, state flags, and cross-file prototypes.

Important APIs, types, and constants: `DRV_NAME`, `DRV_VERSION`, `EHEA_CAPABILITIES`, queue-size constants, packet-size constants, speed constants, BCMC registration flags, memory-region constants, and `EHEA_WATCH_DOG_TIMEOUT` configure driver behavior. `EHEA_BMASK_*` helpers pack and unpack IBM-style bitfields. `struct hw_queue` abstracts page-backed hardware queues. `struct ehea_qp_init_attr`, `ehea_eq_attr`, and `ehea_cq_attr` are PHYP allocation contracts. `struct ehea_adapter` owns the logical adapter, notification EQ, kernel MR, port array, capabilities, and adapter list node. `struct ehea_port` is the netdev-private port state. `struct ehea_port_res` represents one default queue pair and its NAPI, QP/CQ/EQ handles, shared MRs, skb rings, counters, and TX availability state.

Control flow: The header is included by all eHEA units. `ehea_main.c` allocates and mutates adapters, ports, and port resources; `ehea_qmr.c` fills queue/MR internals; `ehea_phyp.c` uses init attributes to marshal hcalls; `ehea_ethtool.c` reads port fields and calls exported sensing/speed helpers.

State and persistence: All state is volatile kernel/firmware state. Persistent-like runtime records include `ehea_fw_handle_array` and `ehea_bcmc_reg_array` used for crash cleanup and re-registration bookkeeping, but they are in-memory only. Port state tracks carrier, speed, MAC, multicast list, queue statistics, reset counts, flags, and work items.

Dependencies and integration: Depends on Linux module, ethtool, vmalloc, VLAN, platform-device, ibmebus, and I/O headers. It is tied to Power/IBM eBus firmware interfaces and to the netdevice stack through `struct net_device`, NAPI, skb arrays, workqueues, wait queues, and link state.

Risks: Queue constants and encoded SG sizes must agree with PHYP allocation and WQE layout. `EHEA_BMASK_IBM` is used everywhere for register/hcall packing; incorrect positions break firmware interaction. `EHEA_MAX_PORT_RES` and `EHEA_MAX_PORTS` bound arrays that are indexed by firmware queue tokens and probed ports. Shared state such as `swqe_avail`, reset flags, and multicast arrays has concurrency exposure across IRQ, NAPI, workqueue, notifier, and sysfs paths.

Test signals: Compile all eHEA units, inspect structure size/layout assumptions on supported Power configs, open/close ports with multiple default QPs, ethtool stats and speed operations, memory hotplug re-registration, crash-shutdown cleanup, multicast/allmulti/promisc changes, and reset work scheduling.
