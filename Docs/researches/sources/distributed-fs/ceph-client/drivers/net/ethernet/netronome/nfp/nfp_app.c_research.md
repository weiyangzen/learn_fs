# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_app.c

## Purpose
Implements the NFP application abstraction: mapping firmware app IDs to driver app types, allocating app containers, dispatching common netdev/app callbacks, managing representor pointer publication, and handling app-level start/stop notifier registration.

## Important APIs, Types, and Functions
- `apps[]` maps `enum nfp_app_id` values to app implementations (`app_nic`, `app_bpf`, `app_flower`, `app_abm`) under build-time config.
- `nfp_app_alloc()` validates app support, allocates `struct nfp_app`, and binds PF/CPP/PCI/type pointers.
- `nfp_app_start()` sets the control vNIC, calls app `.start`, and registers a netdevice notifier; `nfp_app_stop()` unregisters and calls `.stop`.
- `nfp_app_from_netdev()` resolves app pointers from either data vNICs or representors.
- `nfp_app_ctrl_msg_alloc()`, stats wrappers, NDO init/uninit wrappers, and representor helpers provide null-safe dispatch to app callbacks.
- `nfp_app_reprs_set()` publishes representor arrays with RCU under RTNL, with devlink-lock assertions available in the header.

## Control Flow
PF probe reads a firmware app ID, allocates the app, initializes app-specific state, creates vNICs, and eventually starts the app with a control vNIC. Netdev events pass through `nfp_app_netdev_event()`, which handles common feature propagation to representors before delegating to app-specific event handlers.

## State and Persistence Behavior
Owns the runtime `struct nfp_app` and app-private pointer. Representor arrays are RCU-published and protected by the devlink instance lock plus RTNL for update visibility. No disk persistence; app state exists for the PF lifecycle.

## Dependencies and Integration Points
Depends on app implementations, `nfp_main` PF structure, `nfp_net`, `nfp_net_repr`, `nfp_port`, devlink locking, RCU, RTNL, and skb allocation. It is a hub between PCI probe/common netdev code and feature-specific apps.

## Risks
Incorrect app ID support or missing mandatory callbacks blocks probe. Feature propagation iterates representors under RTNL/RCU assumptions. Apps with raw control RX must also provide normal control RX, enforced by `WARN_ON`.

## Test Signals
Probe each supported app type, build with BPF/flower/ABM toggles, create/destroy representors, trigger `NETDEV_FEAT_CHANGE`, verify app `.start` failure unwinds `.stop`, and validate control message allocation headroom behavior for apps using metadata.
