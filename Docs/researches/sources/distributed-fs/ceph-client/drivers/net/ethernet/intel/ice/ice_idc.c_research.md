# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_idc.c

## Purpose
Implements inter-driver communication between the `ice` LAN driver and an auxiliary RDMA driver. It allocates and registers auxiliary devices, exports RDMA resource-management callbacks, forwards events to the auxiliary driver, and manages RDMA device metadata for RoCE.

## Important APIs, types, and functions
- `ice_init_rdma()` allocates `iidc_rdma_core_dev_info`, private RDMA info, a global auxiliary ID from `ice_aux_id`, and fills PCI/hardware identity fields.
- `ice_rdma_finalize_setup()` populates VSI-dependent netdev/vport/QoS fields after VSI and DCB rebuild, then plugs the auxiliary device.
- `ice_plug_aux_dev()` creates an `iidc_rdma_core_auxiliary_dev`, initializes and adds `auxiliary_device`, records it under `pf->adev_mutex`, and sets `ICE_FLAG_AUX_DEV_CREATED`.
- `ice_unplug_aux_dev()` clears the created flag, detaches `cdev->adev`, and unregisters/uninitializes the auxiliary device.
- `ice_send_event_to_aux()` locks the auxiliary device and calls the RDMA driver's `event_handler`.
- Exported RDMA operations include `ice_add_rdma_qset()`, `ice_del_rdma_qset()`, `ice_rdma_request_reset()`, `ice_rdma_update_vsi_filter()`, `ice_alloc_rdma_qvector()`, and `ice_free_rdma_qvector()`.
- `ice_deinit_rdma()` releases xarray ID and RDMA metadata allocations.

## Control flow
Initialization is split: `ice_init_rdma()` prepares generic RDMA state early, while `ice_rdma_finalize_setup()` waits until the main VSI and DCB QoS state are valid before exposing an auxiliary device. The RDMA auxiliary driver calls exported symbols to allocate queue sets, configure filters, request resets, and allocate MSI-X vectors. Events flow from LAN to RDMA through `ice_send_event_to_aux()` under `pf->adev_mutex` and `device_lock()`.

## State and persistence behavior
State is in `pf->cdev_info`, `pf->aux_idx`, `pf->adev_mutex`, `ICE_FLAG_AUX_DEV_CREATED`, and the static xarray allocator `ice_aux_id`. RDMA qsets alter firmware scheduler/resource state through AdminQ. No host persistence is used.

## Dependencies and integration points
Depends on Linux auxiliary bus, Intel IIDC RDMA headers, xarray allocation, DCB QoS setup, VSI lookup/configuration, RDMA filter AdminQ commands, reset scheduling, and the shared IRQ allocator in `ice_irq.c`. The module exports symbols to the RDMA driver.

## Risks
Lifecycle ordering is critical: plugging before VSI/QoS readiness would expose incomplete data, while failing to unplug before freeing `cdev_info` would leave dangling auxiliary state. `ice_send_event_to_aux()` requires task context and uses device locking to avoid driver detach races. RDMA qset operations assume a valid main VSI and enabled RDMA capability.

## Test signals
Probe and remove with RDMA-capable and non-capable devices, auxiliary bus bind/unbind, RDMA qset add/delete, RDMA reset requests, VSI filter toggles, MSI-X allocation/free through RDMA, DCB rebuild followed by finalize setup, and race tests around unplug while events are queued.
