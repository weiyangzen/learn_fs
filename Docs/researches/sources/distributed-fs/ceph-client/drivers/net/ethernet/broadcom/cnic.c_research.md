# `sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/cnic.c`

## Purpose

`cnic.c` is the Linux kernel CNIC core driver for Broadcom/QLogic `bnx2` and `bnx2x` Ethernet devices. It provides common networking offload infrastructure used by upper-layer protocols (ULPs), primarily iSCSI, FCoE, L4/TCP connection management, and hooks for RDMA KCQE dispatch. The driver is not a normal packet data-path driver by itself; it attaches to `bnx2`/`bnx2x` netdevices, registers a `struct cnic_ops` callback table with the Ethernet driver, allocates firmware-visible DMA rings and contexts, exposes UIO mappings for user-space iSCSI support, and brokers work/completion queue entries between ULPs and device firmware.

The implementation has two major hardware families:

- `bnx2` class devices use page-table-backed kernel work queues (KWQ), kernel completion queues (KCQ), 5709 context pages, and explicit context writes via `drv_ctl`.
- `bnx2x` class devices use 16-byte slow-path work queue submissions through the Ethernet driver's `drv_submit_kwqes_16`, storm-memory initialization, context table programming, and separate iSCSI/FCoE KCQs where supported.

## Important APIs, Functions, and Entry Points

Public/exported ULP registration:

- `cnic_register_driver(int ulp_type, struct cnic_ulp_ops *ulp_ops)` installs a global ULP operations table entry under `cnic_lock`, initializes matching existing CNIC devices under RTNL, and uses RCU for readers.
- `cnic_unregister_driver(int ulp_type)` removes the global ULP operations pointer, refuses removal while devices still have that ULP registered, waits for RCU grace, and polls the ULP refcount.
- `cnic_register_device(struct cnic_dev *dev, int ulp_type, void *ulp_ctx)` binds a registered ULP to one CNIC device, stores the ULP context, starts it if CNIC is already up, and tells the Ethernet driver through `cnic_ulp_ctl()`.
- `cnic_unregister_device(struct cnic_dev *dev, int ulp_type)` unbinds a ULP from a device, emits iSCSI IF_DOWN netlink where applicable, waits for pending upcalls, and notifies the Ethernet driver of loaded/inactive state.

Module and netdevice lifecycle:

- `cnic_init()` logs version text, registers `cnic_netdev_notifier`, and creates the single-threaded `cnic_wq`.
- `cnic_exit()` unregisters the notifier, releases lingering UIO devices, and destroys `cnic_wq`.
- `cnic_netdev_event()` handles `NETDEV_REGISTER`, `NETDEV_UP`, `NETDEV_GOING_DOWN`, `NETDEV_UNREGISTER`, and VLAN forwarding events. It creates `cnic_dev` instances for `bnx2`/`bnx2x`, starts and stops hardware, starts and stops ULPs, registers/unregisters with the Ethernet driver, and frees devices.
- `is_cnic_dev()`, `init_bnx2_cnic()`, and `init_bnx2x_cnic()` detect eligible netdevices by ethtool driver name and fill hardware-family-specific function pointers in `struct cnic_local`.

Hardware resource lifecycle:

- `cnic_alloc_dev()` allocates a combined `struct cnic_dev` plus `struct cnic_local`, initializes core callbacks and defaults, and holds the backing netdevice.
- `cnic_start_hw()` maps Ethernet-driver state into CNIC state, allocates resources, starts hardware, opens the L4 connection manager, marks `CNIC_F_CNIC_UP`, and enables interrupts.
- `cnic_stop_hw()` waits briefly for open UIO users, shuts down L2 rings, stops CM, clears `CNIC_F_CNIC_UP`, removes the internal L4 ULP pointer with RCU synchronization, shuts down CM memory, stops hardware, and releases the PCI device.
- `cnic_free_dev()` waits for device references to drain, drops the held netdevice, and frees the CNIC object.

DMA/resource helpers:

- `cnic_alloc_dma()` and `cnic_free_dma()` allocate/free page arrays and optional page tables using coherent DMA memory.
- `cnic_setup_page_tbl()` and `cnic_setup_page_tbl_le()` write hardware page tables in the ordering expected by `bnx2` and `bnx2x`.
- `cnic_alloc_context()`, `cnic_alloc_bnx2x_context()`, and `cnic_free_context()` manage firmware context backing storage.
- `cnic_alloc_bnx2_resc()` and `cnic_alloc_bnx2x_resc()` allocate family-specific KWQ/KCQ/context/UIO/global/iSCSI/FCoE resources.

Queue submission and completion:

- `cnic_submit_bnx2_kwqes()` copies `struct kwqe` entries into the `bnx2` KWQ ring and rings the producer doorbell.
- `cnic_submit_bnx2x_kwqes()` dispatches incoming KWQEs by layer to `cnic_submit_bnx2x_iscsi_kwqes()` or `cnic_submit_bnx2x_fcoe_kwqes()`.
- `cnic_submit_kwqe_16()` builds a `struct l5cm_spe` slow-path element and delegates submission to `bnx2x` via `drv_submit_kwqes_16`.
- `cnic_get_kcqes()` pulls firmware completions from KCQ pages into `cp->completed_kcq`.
- `service_kcqes()` batches completions by layer mask and calls the registered ULP `indicate_kcqes()` callback. It also returns slow-path credits to the Ethernet driver for ramrod completions.

Interrupt and bottom-half handling:

- `cnic_irq()` acks hardware-specific interrupts, then schedules service work.
- `cnic_service_bnx2()`, `cnic_service_bnx2_msix()`, and `cnic_service_bnx2_queues()` service `bnx2` queues and update completion indices.
- `cnic_service_bnx2x()`, `cnic_service_bnx2x_bh_work()`, and `cnic_service_bnx2x_kcq()` service `bnx2x` KCQs, including the second FCoE KCQ on supported chips.
- `cnic_ack_bnx2x_msix()`, `cnic_ack_bnx2x_e2_msix()`, `cnic_arm_bnx2x_msix()`, and `cnic_arm_bnx2x_e2_msix()` handle generation-specific interrupt masking/arming.

Connection manager API installed on `struct cnic_dev`:

- `cnic_cm_open()` allocates the socket table and source-port ID table, initializes hardware CM defaults, sets `dev->cm_create`, `dev->cm_destroy`, `dev->cm_connect`, `dev->cm_abort`, `dev->cm_close`, and `dev->cm_select_dev`, and registers the internal L4 ULP.
- `cnic_cm_create()` reserves a `struct cnic_sock` slot for a ULP connection.
- `cnic_cm_connect()` validates family/address state, chooses route/MTU/VLAN/source port with `cnic_get_route()`, and requests path resolution through iSCSI netlink.
- `cnic_cm_abort()` and `cnic_cm_close()` transition an offloaded connection toward reset or close, sometimes returning `-EALREADY` while remote teardown completes.
- `cnic_cm_destroy()` waits for socket references to drain, releases allocated port state, and clears the socket flags.
- `cnic_cm_select_dev()` routes a destination address and maps the route's real netdevice back to a CNIC device.

BNX2X iSCSI/FCoE operations:

- `cnic_bnx2x_iscsi_init1()` and `cnic_bnx2x_iscsi_init2()` initialize storm-memory parameters, task/R2T/HQ sizing, CQ count, error bitmaps, and emit an INIT completion.
- `cnic_bnx2x_iscsi_ofld1()` validates multi-KWQE iSCSI offload requests, allocates CID/DMA resources, initializes an `iscsi_context`, and replies with success/failure KCQE.
- `cnic_bnx2x_iscsi_update()` sends update ramrods using per-connection KWQE data buffers.
- `cnic_bnx2x_iscsi_destroy()` and `cnic_bnx2x_destroy_ramrod()` coordinate CFC delete ramrods, delayed delete windows, and resource release.
- `cnic_bnx2x_connect()`, `cnic_bnx2x_close()`, and `cnic_bnx2x_reset()` submit L4 TCP connect/close/reset ramrods for iSCSI.
- `cnic_bnx2x_fcoe_init1()`, `cnic_bnx2x_fcoe_ofld1()`, `cnic_bnx2x_fcoe_enable()`, `cnic_bnx2x_fcoe_disable()`, `cnic_bnx2x_fcoe_destroy()`, `cnic_bnx2x_fcoe_fw_destroy()`, and `cnic_bnx2x_fcoe_stat()` implement FCoE function and connection lifecycle for E2+ chips.

UIO integration:

- `cnic_alloc_uio_rings()`, `cnic_init_uio()`, `cnic_uio_open()`, and `cnic_uio_close()` manage `/dev/uio` exposure of BAR/status/L2 ring/L2 buffer mappings.
- UIO open requires `CAP_NET_ADMIN`, refuses concurrent open, and reinitializes L2 rings under RTNL.
- `cnic_chk_pkt_rings()` tracks L2 RX/TX consumer changes and calls `uio_event_notify()` for user-space polling.

## Control Flow and Lifecycle

Device discovery starts in the netdevice notifier. On `NETDEV_REGISTER`, `is_cnic_dev()` queries `ethtool_ops->get_drvinfo()` and creates a CNIC device for `"bnx2"` or `"bnx2x"` if the lower driver exposes `cnic_probe()`. The new device is inserted into `cnic_dev_list`, and `cnic_ulp_init()` calls existing ULP `cnic_init()` hooks.

On `NETDEV_UP`, `cnic_register_netdev()` calls `ethdev->drv_register_cnic()` with either `cnic_bnx2_ops` or `cnic_bnx2x_ops`; then `cnic_start_hw()` allocates DMA resources, programs hardware contexts/rings, opens the connection manager, sets `CNIC_F_CNIC_UP`, enables interrupts, and starts registered ULPs. On `NETDEV_GOING_DOWN`, ULPs are stopped first, hardware is shut down, and the lower Ethernet driver is unregistered. On `NETDEV_UNREGISTER`, the device is removed from `cnic_dev_list`, ULP exit hooks run, references are dropped, and the CNIC object is freed.

For ULP command submission, upper layers call the device's `submit_kwqes`. On `bnx2`, command entries are copied into a KWQ DMA ring and the host producer index is written. On `bnx2x`, the driver decodes the KWQE layer and opcode locally and often converts commands into 16-byte ramrods or immediate synthetic completions. Multi-part iSCSI and FCoE offload requests advance by a `work` count so malformed or incomplete chains can be rejected without losing parser alignment.

Completion processing is interrupt driven. The Ethernet driver or MSI-X interrupt invokes CNIC service callbacks. The service path reads the status block index before KCQ memory (`rmb()`), drains up to `MAX_COMPLETED_KCQE` completions, groups adjacent KCQEs by protocol layer, and invokes the matching ULP callbacks under RCU. L4 completions are consumed by the internal `cm_ulp_ops`, which updates `struct cnic_sock` flags, sends close/searcher-delete/terminate ramrods, and calls ULP connection callbacks.

The iSCSI connection path is two-stage. `cnic_cm_connect()` first derives route, VLAN, MTU, address family, and source port, then asks the iSCSI ULP to resolve path data through `iscsi_nl_send_msg()`. On `ISCSI_UEVENT_PATH_UPDATE`, `cnic_iscsi_nl_msg_recv()` copies MAC/source IP/VLAN results to the socket. If a valid MAC is present, `cnic_cm_set_pg()` offloads or updates a page context; when the page-context completion arrives, `cnic_cm_process_offld_pg()` submits the actual TCP connect KWQE. If no valid MAC is returned, it reports connect completion without offload.

BNX2X connection teardown is deliberately delayed in some cases. `cnic_bnx2x_iscsi_destroy()` and `cnic_bnx2x_fcoe_destroy()` set `CTX_FL_DELETE_WAIT` and queue `cnic_delete_task()` so firmware CFC delete happens after a two-second safety window from termination. `cnic_delete_task()` also handles `CNIC_CTL_STOP_ISCSI_CMD` by stopping the iSCSI ULP and notifying the Ethernet driver.

## State and Persistence Behavior

All state is volatile kernel/driver state; the file does not persist configuration to disk. Persistent effects are limited to hardware registers, firmware context memory, DMA memory visible to the device, UIO device registration, netdevice notifier registration, and ULP/Ethernet-driver callbacks.

Important state containers:

- Global `cnic_dev_list` tracks live CNIC devices and is protected by RTNL plus `cnic_dev_lock`.
- Global `cnic_udev_list` tracks UIO objects that can temporarily outlive a CNIC device when user-space has a device open.
- Global `cnic_ulp_tbl[]` holds registered ULP drivers under `cnic_lock` and RCU.
- Per-device `struct cnic_local` stores lower-driver pointers, ULP handles/flags, DMA descriptors, KWQ/KCQ state, status blocks, UIO state, connection tables, CID tables, context arrays, hardware-family function pointers, and interrupt callbacks.
- `struct cnic_sock` entries in `cp->csk_tbl` carry L4 connection state: flags, CIDs, route-derived IP/MAC/VLAN/MTU/source port, KWQE scratch buffers, and ULP context.
- `struct cnic_context` entries in `cp->ctx_tbl` track firmware CIDs, per-connection KWQE data buffers, wait queues, delayed delete flags, timestamps, and protocol ownership.

Reference and concurrency state is managed by atomics and bit flags. Device refs (`cnic_hold`/`cnic_put`), socket refs (`csk_hold`/`csk_put`), and ULP refs (`ulp_get`/`ulp_put`) prevent immediate teardown while callbacks may run. Bit flags such as `CNIC_F_CNIC_UP`, `ULP_F_START`, `ULP_F_CALL_PENDING`, `SK_F_CONNECT_START`, `SK_F_OFFLD_SCHED`, `SK_F_OFFLD_COMPLETE`, `SK_F_PG_OFFLD_COMPLETE`, `CTX_FL_OFFLD_START`, and `CTX_FL_DELETE_WAIT` encode lifecycle transitions.

## Dependencies and Integration Points

Kernel subsystems:

- Netdevice notifier, RTNL, VLAN helpers, IPv4/IPv6 route lookup, destination cache, and `net_device` references.
- PCI device references, coherent DMA allocation, IRQ registration/synchronization, workqueues, wait queues, atomics, spinlocks, mutexes, RCU, bitops, memory barriers, and UIO.
- iSCSI userspace/netlink definitions through `<scsi/iscsi_if.h>`.

Driver-local and firmware headers:

- `cnic_if.h` defines the public CNIC/ULP/Ethernet-driver interface.
- `bnx2.h`, `bnx2x/bnx2x*.h`, `57xx_iscsi_*`, `bnx2fc_constants.h`, `cnic.h`, and `cnic_defs.h` provide chip registers, firmware HSI structures, opcodes, context structures, and macros.

Lower Ethernet driver integration:

- `cnic_probe()` discovers `struct cnic_eth_dev` from `bnx2`/`bnx2x`.
- `drv_register_cnic()` and `drv_unregister_cnic()` attach/detach CNIC callbacks.
- `drv_ctl()` handles indirect register/context writes, L2 ring start/stop, ULP register/unregister notifications, credits, stop notifications, and completion callbacks.
- `drv_submit_kwqes_16()` submits `bnx2x` slow-path work elements.
- `drv_get_fc_npiv_tbl()` supplies FCoE NPIV data.

ULP integration:

- iSCSI, FCoE, RDMA, and L4 use `struct cnic_ulp_ops` callbacks such as `cnic_init`, `cnic_exit`, `cnic_start`, `cnic_stop`, `indicate_kcqes`, `indicate_netevent`, `cnic_get_stats`, `iscsi_nl_send_msg`, and connection-manager callbacks.
- The internal L4 ULP (`cm_ulp_ops`) consumes L4 KCQEs and turns them into ULP connection callbacks.

## Risks and Edge Cases

- The file is highly sensitive to hardware/firmware ABI details. Context layout, byte ordering, ring index skip rules, status block offsets, and storm-memory offsets must match the included HSI headers and device generation.
- Many operations run under asynchronous netdevice, interrupt, RCU, workqueue, and UIO-open paths. Bugs in flag ordering or missing synchronization could cause use-after-free, missed completions, or duplicate close/offload requests.
- Several waits are polling/time-limited (`msleep`, `udelay`, `wait_event_timeout`) and log warnings rather than fully recovering if firmware does not complete delete, ring setup/halt, or refcount drain.
- `cnic_submit_bnx2x_iscsi_kwqes()` and `cnic_submit_bnx2x_fcoe_kwqes()` continue processing after many per-KWQE failures and return 0 overall, relying on synthetic error KCQEs for ULP cleanup.
- Resource allocation is multi-stage; most error paths call broad cleanup helpers, but any new allocation added to `struct cnic_local` must be wired into both family-specific error exits and `cnic_free_resc()`.
- UIO state can outlive CNIC device state. `cnic_free_resc()` intentionally leaves ring buffers allocated if a UIO file is open, so future changes must respect `udev->dev`, `udev->uio_dev`, and list lifetime.
- `cnic_cm_select_dev()` obtains and immediately puts the CNIC device before returning the pointer, matching existing API expectations but risky if callers assume a held reference.
- Source port allocation assumes the configured range length behaves correctly with bitmap `next` wrap logic; changes to range constants should preserve power-of-two assumptions in `cnic_alloc_new_id()`.
- FCoE support depends on `CNIC_SUPPORTS_FCOE(bp)`, which references a local `bp` symbol through a macro from the header. This macro is concise but fragile if reused where `bp` is not in scope.

## Test Signals and Validation Ideas

There are no in-file self-tests. Useful validation signals are mostly integration-level:

- Build coverage for configurations with and without VLAN, IPv6, UIO, iSCSI, FCoE-capable `bnx2x`, MSI-X, and non-MSI-X paths.
- Static analysis around RCU dereferences, lock ordering (`cnic_lock`, `cnic_dev_lock`, RTNL, `cnic_ulp_lock`), DMA allocation error paths, and array bounds for `l5_cid`, FCoE CIDs, and KCQ/KWQ indices.
- Runtime attach/detach tests: load module, register iSCSI/FCoE ULPs, bring `bnx2`/`bnx2x` netdevices up/down, unregister devices, unload module, and verify no refcount drain warnings.
- iSCSI path tests for IPv4, IPv6, VLAN, invalid MAC/path resolution failure, source-port conflict, connection close, abort, remote reset, and hardware reset/parity error simulation.
- FCoE tests on E2+ hardware for init/offload/enable/disable/destroy/stat and function destroy after outstanding connection teardown.
- UIO tests for CAP_NET_ADMIN enforcement, single-open behavior, ring reinitialization on open, event notifications on L2 ring consumer movement, and teardown while UIO is open.
- Fault injection for DMA allocation failures, `request_irq()` failure, `drv_register_cnic()` failure, missing iSCSI support (`CNIC_DRV_STATE_NO_ISCSI`), and firmware ramrod timeout.
