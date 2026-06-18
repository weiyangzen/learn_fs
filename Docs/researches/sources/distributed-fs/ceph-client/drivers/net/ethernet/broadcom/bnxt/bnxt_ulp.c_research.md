# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ulp.c

## Purpose
Manages bnxt upper-layer protocol auxiliary devices, primarily RDMA/RoCE and fwctl. It allocates auxiliary-device identities, publishes `bnxt_en_dev` objects, handles ULP registration and firmware messaging, reserves MSI-X/stat resources, routes async events, and coordinates ULP stop/start around netdev and firmware-reset transitions.

## Important APIs, Types, And Functions
Exports include `bnxt_register_dev()`, `bnxt_unregister_dev()`, `bnxt_send_msg()`, `bnxt_register_async_events()`, resource getters/setters for ULP MSI-X and stat contexts, stop/start/IRQ helpers, and auxiliary lifecycle functions `bnxt_aux_devices_init()`, `bnxt_aux_devices_add()`, `bnxt_aux_devices_del()`, `bnxt_aux_devices_uninit()`, `bnxt_auxdev_id_alloc()`, and `bnxt_auxdev_id_free()`. Internal `struct bnxt_aux_device` names supported aux devices, while `bp->edev[]`, `bp->aux_priv[]`, and `bp->auxdev_state[]` track active objects.

## Control Flow
Initialization allocates a global IDA id, creates initialized-but-not-added auxiliary devices for supported slots, allocates `bnxt_en_dev` and `bnxt_ulp`, copies bnxt device capabilities into the exported object, and records an INIT state. Add transitions INIT devices to ADD through `auxiliary_device_add()`. Delete removes active auxiliary devices and returns them to INIT. Uninit releases initialized devices; final memory cleanup occurs in the auxiliary device release callback.

ULP drivers call `bnxt_register_dev()` with operation callbacks and a handle. The driver validates IRQ/resource availability, installs ops under RCU, optionally reconfigures the default VNIC for dual VNIC mode if the netdev is open, records requested MSI-X count, and fills vector metadata. Unregister clears async registration, removes ops with RCU synchronization, and resets event fields. Stop/start loops over active aux devices, sets `BNXT_EN_FLAG_ULP_STOPPED`, and calls auxiliary driver suspend/resume where appropriate.

## State And Persistence Behavior
State is in memory: auxiliary device state slots, exported device descriptors, ULP callback pointers, requested MSI-X count, stat context reservations, async event bitmaps, max event id, stopped flags, and cached bnxt state. `bnxt_register_async_events()` uses a write memory barrier before publishing the max event id; `bnxt_ulp_async_events()` uses a read barrier before testing the bitmap. Firmware registration through `bnxt_hwrm_func_drv_rgtr()` persists async event subscriptions in device firmware until cleared.

## Dependencies And Integration Points
This file integrates with the Linux auxiliary bus, IDA allocation, netdev instance locking, RCU callback publication, HWRM command transport, firmware async event registration, bnxt VNIC configuration, IRQ/MSI-X table layout, RoCE capability flags, and auxiliary drivers that implement suspend/resume and ULP ops.

## Risks
The lifecycle crosses several ownership systems: auxiliary bus release semantics, bnxt private arrays, RCU ops pointers, and netdev locks. Misordered cleanup can leak aux devices or leave stale `bp->edev[]` pointers. MSI-X vectors must match current IRQ tables after reset. Async bitmap publication uses memory ordering that must remain paired. `bnxt_send_msg()` copies firmware responses into caller buffers and depends on response length clamping.

## Test Signals
Useful coverage includes loading/unloading RDMA and fwctl auxiliary drivers, registering/unregistering while the netdev is open and closed, firmware reset with ULP stop/start and IRQ restart, async event delivery only for subscribed event ids, MSI-X reservation pressure, auxiliary add failure unwind, and builds without RoCE capability.
