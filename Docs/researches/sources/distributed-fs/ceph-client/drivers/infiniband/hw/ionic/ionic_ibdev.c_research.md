# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_ibdev.c

Purpose: Ionic RDMA ib_device registration and device lifecycle glue. This file binds an Ethernet Ionic LIF to the RDMA core, fills device attributes and ops, initializes resource allocators and tables, creates admin/event infrastructure, registers with ib_core, and tears everything down on remove/reset.

Important APIs/functions: the file provides the driver-facing add/remove/reset hooks for the Ionic RDMA device and wires the `ib_device_ops` table to control-path, datapath, mmap, MR/MW, AH, CQ, QP, ucontext, PD, query, port, and stats helpers declared in `ionic_ibdev.h`.

Control flow: probe-style setup obtains LIF configuration via `ionic_fill_lif_cfg()`, allocates and initializes `struct ionic_ibdev`, seeds xarrays and ID allocators, creates admin queues/EQs, sets RDMA core attributes, registers verbs ops, initializes optional stats, then registers the ib_device. Teardown reverses registration, disables/cleans stats, destroys admin/EQ resources, drains reset/admin work, and frees ID/xarray state. Reset paths coordinate with admin state so in-flight work is paused or killed before objects are re-created or failed.

State and persistence: central state is `struct ionic_ibdev`: `lif_cfg`, QP/CQ xarrays, resource ID allocators, admin/EQ vectors, reset work, admin delayed work, stats pointers, and UDMA allocation cursors. State exists for the lifetime of the RDMA device and is rebuilt from LIF identity after reprobe/reset.

Dependencies and integration: integrates with Linux RDMA core, the Ionic Ethernet LIF/device identity, admin/control/datapath/stat modules, workqueues, xarrays, IDA allocators, and netdev/lif helper functions.

Risks: lifecycle ordering is the main risk: ib_device unregister must happen before freeing queues and resource tables visible to verbs callbacks. Reset/admin work needs clear state transitions to avoid completing commands against freed objects. Device limits must match firmware identity fields or user-visible caps can exceed allocatable resources.

Test signals: module probe/remove, RDMA device visibility in `ibv_devices`, uverbs context creation, reset during active QPs/CQs, admin queue failure injection, stats ops installation, and leak checks for xarrays/IDAs/workqueues.
