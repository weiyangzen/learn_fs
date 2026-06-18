# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_client.c

## Purpose

`i40e_client.c` is the LAN-driver side of the auxiliary client interface, primarily for the iWARP/RDMA client. It creates an `i40e_info` view of the PF, exposes callback operations to the client, registers an auxiliary device named `iwarp`, opens/closes the client when service state allows, forwards VF virtual-channel events, and maps RDMA queue/vector interrupts into i40e hardware registers.

## Important APIs, Types, And Functions

- Global state: `i40e_devices`, `i40e_device_mutex`, and `i40e_client_ida`.
- `i40e_lan_ops` exposes `virtchnl_send`, `setup_qvlist`, `request_reset`, and `update_vsi_ctxt`.
- `i40e_client_get_params()` derives runtime MTU and priority-to-traffic-class/queue-set-handle QoS parameters from DCB/VSI state.
- Notification helpers call client callbacks for VF messages, L2 parameter changes, netdev close, VF reset, VF enable, and VF capability checks.
- `i40e_register_auxiliary_dev()` allocates and registers the auxiliary device; `i40e_auxiliary_dev_release()` frees the ID and wrapper.
- `i40e_client_add_instance()` builds `pf->cinst`, fills `lan_info`, copies MAC/version/firmware/MSI-X data, and registers the auxiliary `iwarp` device.
- `i40e_lan_add_device()` and `i40e_lan_del_device()` manage PF list membership and client instance lifetime.
- `i40e_client_subtask()` opens the client on service events and keeps the VSI TCP enable queue option in sync with netdev up/down state.
- `i40e_client_virtchnl_send()` sends `VIRTCHNL_OP_RDMA` messages to a VF using `i40e_aq_send_msg_to_vf()`.
- `i40e_client_setup_qvlist()` programs CEQ/AEQ interrupt routing registers for client-owned vectors.
- Exported symbols `i40e_client_device_register()` and `i40e_client_device_unregister()` are used by the RDMA auxiliary client driver.

## Control Flow

PF registration calls `i40e_lan_add_device()`, which adds a list node, creates a client instance, registers the auxiliary device, sets `__I40E_CLIENT_SERVICE_REQUESTED`, and schedules service. The iWARP auxiliary driver probes and calls `i40e_client_device_register()`, which stores the client pointer and schedules service again. `i40e_client_subtask()` runs in the i40e service path; if the PF is not down or config-busy and the netdev is registered, it calls the client's `open()` and marks the instance opened only if open succeeds.

After open, event notification helpers gate every callback on `pf->cinst`, `client`, the specific operation pointer, and `__I40E_CLIENT_INSTANCE_OPENED`. Close paths call the client `close()` callback, clear the opened bit, and release any queue-vector list. Unregister waits for service scheduling state, closes if needed, clears the client pointer, and releases the service bit.

The queue/vector setup flow validates vector ownership, saves a copy of the qvlist, writes `PFINT_LNKLSTN`, `PFINT_CEQCTL`, and `PFINT_AEQCTL`, then flushes hardware. On validation failure it frees the stored list and returns `-EINVAL`.

## State And Persistence Behavior

Persistent driver state includes `pf->cinst`, `cdev->state` bits, `cdev->lan_info`, `ldev->qvlist_info`, the global LAN-device list, and auxiliary device IDs. Hardware state includes interrupt linkage/control registers and VSI queue option state. This state lasts until netdev close, client unregister, PF removal, reset, or LAN device deletion. No state is persisted to NVM.

## Dependencies And Integration Points

- Depends on `include/linux/net/intel/i40e_client.h` for client ABI types and callback signatures.
- Depends on `i40e.h` for PF/VSI state bits, register macros, queue constants, and service scheduling.
- Uses Admin Queue wrappers from `i40e_common.c`, especially `i40e_aq_send_msg_to_vf()`, `i40e_aq_get_vsi_params()`, and `i40e_aq_update_vsi_params()`.
- Integrates with the Linux auxiliary bus and the RDMA client implementation under `drivers/infiniband/hw/irdma/i40iw_if.c`.

## Risks

- `i40e_lan_del_device()` assumes `pf->cinst` exists when dereferencing `pf->cinst->lan_info.aux_dev`.
- `i40e_client_device_unregister()` uses a busy-wait on `__I40E_SERVICE_SCHED`; incorrect service-bit handling can stall unregister.
- The qvlist setup validates vector ownership but not all semantic combinations of CEQ/AEQ/ITR values.
- Client callback execution is cross-subsystem and must respect locking and reset state.
- `i40e_client_update_vsi_ctxt()` rejects VF VSI updates and only supports TCP enable.
- The service task sets the opened bit before calling `open()` and clears it on failure; callback implementations must tolerate this lifecycle ordering.

## Test Signals

- Probe/remove and auxiliary-device bind/unbind loops should leave no leaked `i40e_client_instance`, auxiliary ID, or qvlist memory.
- RDMA client open/close tests should verify callbacks fire only when opened.
- SR-IOV tests should cover VF message, VF reset, VF enable, and `vf_capable()` flows.
- MSI-X/qvlist tests should include valid vectors, out-of-range vectors, CEQ disabled entries, AEQ entries, and register cleanup on close.
- Netdev up/down and MTU/DCB changes should trigger L2 parameter refresh and TCP enable bit updates.
