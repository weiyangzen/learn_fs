<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_main.c

## Purpose

Provides PVRDMA module lifecycle, PCI probe/remove, RDMA device registration, interrupt handlers, async event dispatch, GID binding, netdevice pairing, and sysfs attributes.

## Important APIs, Types, And Functions

Key flows are `pvrdma_pci_probe()`, `pvrdma_pci_remove()`, `pvrdma_register_device()`, `pvrdma_alloc_intrs()`, `pvrdma_intr0_handler()`, `pvrdma_intr1_handler()`, `pvrdma_intrx_handler()`, `pvrdma_add_gid()`, `pvrdma_del_gid()`, netdevice notifier/work handlers, `pvrdma_init()`, and `pvrdma_cleanup()`. `pvrdma_dev_ops` wires all RDMA core operations to PVRDMA implementations; `pvrdma_dev_srq_ops` is installed conditionally when the backend supports SRQ.

## Control Flow

Probe allocates `pvrdma_dev`, enables PCI, requests regions, sets 64-bit DMA, maps registers and driver UAR, allocates the DMA-coherent shared region plus command/response slots, creates async and CQ notification rings, writes the DSR address to the device, validates RoCE support, locates the sibling VMXNET3 netdev, allocates interrupts, initializes UAR/GID tables, activates the device, registers the IB device, and registers a netdevice notifier.

Interrupt vector 0 completes command responses. Vector 1 drains async events and dispatches QP/CQ/SRQ/device events with refcount protection. Later vectors drain CQ notification events and invoke CQ completion handlers. Remove unregisters netdevice and IB state, disables interrupts, resets the device, frees coherent/page-directory state, unmaps MMIO, frees tables, and disables PCI.

## State And Persistence Behavior

Persistent module state includes an ordered event workqueue and a global `pvrdma_device_list` protected by a mutex. Per-device persistent state includes mapped MMIO, shared DMA region, rings, command slots, object lookup tables, GID table, UAR table, netdev reference, interrupt vectors, and registered `ib_device`. Runtime GID bindings are mirrored in `sgid_tbl` and in backend state through create/destroy bind commands.

## Dependencies And Integration Points

Integrates PCI, DMA coherent memory, MSI-X/MSI/INTx IRQ allocation, RDMA core registration, netdevice notifiers, VMXNET3 pairing, sysfs device attributes, and all local PVRDMA verbs implementations.

## Risks And Edge Cases

Probe has many staged resources and must unwind in exact reverse order. Netdevice association assumes the VMXNET3 function is same bus/slot/function 0. Event handlers use modulo lookups and refcounts; handle-table mismatch can misdispatch events. On NETDEV_UNREGISTER, `dev->netdev` becomes NULL, so remove must tolerate prior notifier cleanup. Device activation depends on ordered DSR register writes and barriers.

## Test Signals

Test probe failure at each allocation/mapping/command stage, successful attach to paired VMXNET3, interrupt fallback from MSI-X to MSI/INTx, async QP/CQ/SRQ/device events, netdev up/down/register/unregister, GID add/delete, sysfs attributes, and remove after partially initialized or active devices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_main.c -->
