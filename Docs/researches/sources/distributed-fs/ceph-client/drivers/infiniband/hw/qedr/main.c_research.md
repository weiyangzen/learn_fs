# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/main.c

## Purpose
`main.c` is the QEDR driver's module entry, device lifecycle, RDMA core registration, interrupt setup, hardware start/stop, asynchronous event dispatch, and qede notification bridge. It turns a `qed_dev` plus `net_device` into an `ib_device` with either RoCE or iWARP operation extensions.

## Important APIs, Types, And Functions
It defines the common `qedr_dev_ops` `ib_device_ops` table, iWARP-specific ops (`iw_connect`, listen, accept/reject, QP ref hooks), and RoCE-specific ops (`query_pkey`, RoCE immutable port flags). Device lifecycle functions include `qedr_add`, `qedr_remove`, `qedr_open`, `qedr_close`, `qedr_shutdown`, and `qedr_notify`. Hardware/resource functions include `qedr_alloc_resources`, `qedr_free_resources`, `qedr_init_hw`, `qedr_stop_hw`, `qedr_setup_irqs`, `qedr_req_msix_irqs`, `qedr_irq_handler`, and `qedr_set_device_attr`.

## Control Flow
Module init registers a `qedr_driver` with qede. On add, the driver allocates an RDMA device, obtains QED RDMA ops, reads device info, rejects iWARP CMT unless lower-layer affinity allows it, determines CNQ count, sets PCI atomic capability, allocates SGID/CNQ/status-block resources, starts QED RDMA with CNQ PBLs and async callbacks, queries device attributes, requests MSI-X interrupts, registers the `ib_device`, and dispatches a port-active event. Remove unregisters the RDMA device first to stop clients, then stops QED RDMA, frees IRQs/resources, restores iWARP affinity if needed, and deallocates the RDMA device.

The IRQ handler disables the status block, reads hardware and software CNQ consumers, consumes CQ handles from the QED chain, validates CQ signatures, invokes RDMA completion handlers, increments `cnq_notif` after handlers finish to coordinate CQ destruction, updates the hardware producer, and re-enables interrupts. Affiliated async events translate QED RoCE/iWARP event codes into `ib_event` callbacks for CQs, QPs, or SRQs.

## State And Persistence Behavior
All state is runtime device state: CNQ arrays, status blocks, SGID table, xarrays for SRQs/QPs, iWARP workqueue, doorbell/DPI information, `enet_state`, GSI pointers, and cached capability attributes. `enet_state` prevents duplicate port-active/port-error events. No persistent on-disk state exists.

## Dependencies And Integration Points
This file depends on RDMA core registration and object-size macros, qede's RDMA driver registration API, QED RDMA/common ops, PCI/MSI-X, DMA coherent memory, QED chains/status blocks, netdev events, and helper functions from `verbs.c`, `qedr_iw_cm.c`, and `qedr_roce_cm.c`. It exports sysfs attributes `hw_rev` and `hca_type` through the RDMA device group.

## Risks And Test Signals
Risks center on lifecycle ordering: clients must be unregistered before hardware teardown, IRQ handlers must not race CQ destruction, and iWARP workqueue/QP references must be drained before resources disappear. `qedr_add` logs through `dev` after `ib_dealloc_device` in the failure path, which should be reviewed for use-after-free risk depending on macro expansion. Test signals include module load/unload loops, qede up/down/change-MTU/change-MAC notifications, MSI-X interrupt traffic under RDMA load, CQ destruction under interrupt pressure, RoCE and iWARP registration smoke tests, and fault injection for each staged add failure label.
