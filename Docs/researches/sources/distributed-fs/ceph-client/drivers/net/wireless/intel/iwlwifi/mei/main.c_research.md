# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/main.c

## Purpose

`mei/main.c` implements the Intel wireless host-to-CSME SAP transport over the Linux MEI client bus. It binds to the WLAN MEI UUID, allocates DMA shared memory, starts the SAP handshake, exports the iwlwifi-facing `iwl_mei_*` API, and coordinates NIC ownership, AMT state, NVM retrieval, PLDR reset, rfkill/link notifications, CSME packet forwarding, netdev RX handler registration, debugfs, probe, and teardown.

## Important APIs, Types, and Functions

Central state is `struct iwl_mei`, which holds wait queues, shared-memory pointers, cached firmware data, RCU filters, ownership flags, work items, sequence counters, and debugfs state. `struct iwl_mei_cache` buffers iwlwifi-provided callbacks and configuration while no MEI device is bound. Exported APIs include `iwl_mei_is_connected()`, `iwl_mei_get_nvm()`, `iwl_mei_pldr_req()`, `iwl_mei_get_ownership()`, `iwl_mei_alive_notif()`, association/rfkill/NIC/MCC/SAR/netdev setters, device-up/down notification, and driver register/unregister functions.

Key helpers allocate/init the SAP shared area (`iwl_mei_alloc_shared_mem()`, `iwl_mei_init_shared_mem()`), write circular queues (`iwl_mei_write_cyclic_buf()`), signal CSME with `SAP_ME_MSG_CHECK_SHARED_AREA`, parse inbound SAP notification/data queues, and dispatch SAP message handlers.

## Control Flow

Probe allocates `struct iwl_mei`, initializes work and wait queues, maps a SAP v4 shared area with fallback to v3, initializes queue layout, enables the MEI client, registers the RX callback, sends `SAP_ME_MSG_START`, and finally publishes `iwl_mei_global_cldev`. `SAP_ME_MSG_START_OK` validates the negotiated SAP version and sets the connected bit. Later `AMT_STATE` starts the cached initial configuration flow: WiFi-driver-up, ownership query, cached host link, MCC, SAR, NIC info, and rfkill messages.

SAP payloads move through shared circular queues. Host-to-CSME notification/data writes update write pointers and then send a MEI doorbell unless throttled. CSME-to-host doorbells cause notification queue parsing, per-message dispatch, data queue parsing into skbs, and deferred `dev_queue_xmit()` outside `iwl_mei_mutex`.

## State and Persistence Behavior

Long-lived state is split between global connection state, the singleton MEI device pointer, shared DMA queue metadata, cached iwlwifi configuration, and RCU-published netdev/filter pointers. Ownership, AMT enablement, link-protection, device-down, PLDR, and throttle flags determine whether messages are sent or callbacks are invoked. Remove carefully sends `HOST_GOES_DOWN`, waits for host-to-ME queues to drain, clears the connected bit under `data_q_lock`, unregisters RX handlers, disables MEI outside the mutex, cancels work, wakes waiters, unmaps DMA memory, and frees cached dynamic state.

## Dependencies and Integration Points

This file integrates the MEI client bus, iwlwifi's `iwl-mei.h` callback contract, Linux netdev RX handlers, RCU, wait queues, debugfs, skbs, cfg80211/mac80211 connection data, and SAP protocol definitions in `sap.h`. `net.c` supplies the packet filters and DHCP copy path. Tracepoints in `trace.h` and `trace-data.h` instrument SAP commands and packet payloads.

## Risks and Edge Cases

The file is concurrency-heavy: `iwl_mei_mutex`, `data_q_lock`, RCU, RTNL, work cancellation, and MEI RX callback shutdown must remain ordered. Circular queue pointer validation protects against corrupt CSME state, but full/empty accounting uses simple read/write positions and no reserved slot, so queue-size assumptions are important. `iwl_mei_send_sap_msg_payload()` calls `iwl_mei_write_cyclic_buf(q_head, notif_q, ...)`, whose first parameter is typed as `struct mei_cl_device *`; the function does not dereference it except in error paths, making the call compile but fragile if logging is refactored. Timeout-based NVM, ownership, and PLDR waits must tolerate device removal and wakeups during teardown.

## Test Signals

Useful signals are MEI bind/unbind, suspend/resume, AMT enabled/disabled transitions, ownership steal/retake, PLDR success/failure, netdev replacement under RTNL, SAP v3/v4 allocation fallback, queue wraparound, invalid pointer/length injection, NVM timeout, and packet forwarding with CSME filters enabled. Dynamic validation should watch tracepoints, rfkill callbacks, absence of IOMMU errors on remove, and no UAF after RX-handler unregister.
