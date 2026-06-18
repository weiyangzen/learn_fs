# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_main.c

Purpose: Provides SoftiWARP module initialization, RDMA device registration, netdevice integration, per-CPU TX worker placement, module parameters, and the RDMA device operations table binding the provider to RDMA core and IWCM.

Important APIs/types/functions: Global tunables include `zcopy_tx`, `try_gso`, `loopback_enabled`, `mpa_crc_required`, `mpa_crc_strict`, `siw_tcp_nagle`, `mpa_version`, and `peer_to_peer`. `siw_device_ops` registers all verbs and IWCM callbacks. `siw_device_create()` allocates and initializes `struct siw_device`, RDMA identity, netdev binding, limits, xarrays, counters, and ops. `siw_newlink()` implements RDMA netlink `newlink` for type `siw`. `siw_netdev_event()` unregisters on netdev removal and emits port events on address changes. `siw_get_tx_cpu()` and `siw_put_tx_cpu()` balance QP TX assignment across NUMA-local worker CPUs.

Control flow: Module init validates constants, initializes CPU masks, starts CM and TX workers, registers a netdevice notifier, and registers RDMA link ops. Users create SIW devices via RDMA netlink; each device is attached one-to-one to a qualified netdev. Module exit stops workers, unregisters notifier/link ops/driver, exits CM, and frees CPU masks.

State and persistence behavior: Module-level state consists of CPU masks, per-CPU use counters, TX kthreads, and RDMA link/notifier registrations. Device state is in RDMA core and `siw_device`; there is no disk persistence.

Dependencies/integration: Integrates with Linux netdevice events, RDMA core registration, RDMA netlink, kthreads, NUMA CPU topology, and all SIW verbs/CM/QP functions. Qualifies Ethernet, IEEE802, ARPHRD_NONE, and optional loopback netdevs.

Risks: Init error unwinding spans CM, TX threads, CPU masks, and notifiers. TX CPU selection must handle offline CPUs and no-worker cases. Netdev unregister races can interact with active QPs and CM endpoints. Device naming and `dev_id` are process-local and incrementing.

Test signals: Module load/unload, rdma link add/delete for eligible and ineligible netdevs, loopback enable behavior, CPU hotplug or offline TX CPU reassignment, netdev unregister, address-change event delivery, and failure injection during init.
