# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_app.h

## Purpose
Declares the NFP application interface used by app implementations and common driver code. It defines app IDs, callback tables, app container state, inline dispatch helpers, control-message tracing wrappers, devlink/eswitch/SR-IOV hooks, and shared NIC app callbacks.

## Important APIs, Types, and Functions
- `enum nfp_app_id` identifies core NIC, BPF NIC, flower NIC, and active buffer management NIC firmware apps.
- `struct nfp_app_type` is the main callback contract for init/clean, vNIC lifecycle, representors, MTU/statistics, start/stop, netdev events, control messages, TC/BPF/XDP, SR-IOV, eswitch mode, and device lookup.
- `struct nfp_app` stores PF/CPP/PCI backpointers, control vNIC, RCU representor arrays, app type, control MTU, netdev notifier, and app-private data.
- Inline helpers null-check and dispatch callback families, including `nfp_app_vnic_alloc()`, `nfp_app_repr_open()`, `nfp_app_setup_tc()`, `nfp_app_xdp_offload()`, `nfp_app_sriov_enable()`, and `nfp_app_dev_get()`.
- Control TX/RX wrappers trace devlink hardware messages and call `nfp_ctrl_tx()`, `__nfp_ctrl_tx()`, or app RX callbacks.

## Control Flow
Common code treats apps polymorphically through this header. Probe allocates and initializes an app, vNIC setup calls app allocation/init callbacks, netdev operations call NDO/TC/BPF/MTU wrappers, control datapath calls control RX/TX wrappers, and devlink/SR-IOV operations delegate to app-specific hooks when present.

## State and Persistence Behavior
Defines runtime-only state. `reprs[]` is RCU-protected and app lock assertions are tied to the devlink instance lock. Control message wrappers only trace and dispatch; persistence is in firmware/app state outside this header.

## Dependencies and Integration Points
Includes devlink trace support and representor definitions. It is included by most NFP common/app modules and connects Linux netdev, devlink, TC, BPF, XDP, SR-IOV, representors, and firmware control messaging.

## Risks
Callback return defaults vary (`0`, `-EINVAL`, `-EOPNOTSUPP`, `NULL`) and callers must interpret them correctly. App lock assumptions matter for representor access. `nfp_app_ctrl_has_meta()` assumes non-null app in some callers; control-vNIC users must only call it after app allocation.

## Test Signals
Compile all config permutations, exercise absent callbacks, verify devlink hwmsg tracepoints on control messages, test TC/BPF/XDP offload fallback errors, SR-IOV enable/disable delegation, and representor lookup/redirection.
