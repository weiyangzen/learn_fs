# sources/distributed-fs/ceph-client/net/bridge/br_private_cfm.h

## Purpose
`br_private_cfm.h` defines the bridge Connectivity Fault Management internal API and state objects. It bridges CFM netlink/UAPI concepts to in-kernel MEP, peer MEP, continuity-check, transmit, receive, and status tracking.

## Important APIs, types, and functions
- Configuration structs include `br_cfm_mep_create`, `br_cfm_mep_config`, `br_cfm_maid`, `br_cfm_cc_config`, and `br_cfm_cc_ccm_tx_info`.
- Status structs include `br_cfm_mep_status` and `br_cfm_cc_peer_status`.
- Runtime structs are `br_cfm_mep` and `br_cfm_peer_mep`, which hold hlist membership, instance IDs, RCU bridge-port pointers, peer lists, delayed work, sequence numbers, status flags, RDI, and RCU teardown.
- Exported APIs create/delete MEPs, set MEP and CC config, add/remove peer MEPs, set RDI, and control CCM transmission.

## Control flow
This header is declarative. Callers such as CFM netlink parsing create or configure MEP instances, then CFM implementation code uses delayed work to transmit CCMs until `ccm_tx_end` and to detect missed peer CCMs. Status is later filled into netlink dumps through CFM helpers declared in `br_private.h`.

## State and persistence
CFM state is in `br->mep_list` when `CONFIG_BRIDGE_CFM` is enabled. Per-MEP state tracks configuration, peer list, residence port, transmit lifetime, sequence counters, and local status. Per-peer state tracks received CCM status and missed-count detection. State is in-memory only and protected by the CFM implementation's locking/RCU rules.

## Dependencies and integration points
The header depends on bridge internals and `<uapi/linux/cfm_bridge.h>`. It integrates with `br_netlink.c` through CFM `AF_BRIDGE` attributes and with bridge port lifetime through RCU `b_port` pointers.

## Risks and edge cases
Delayed work and RCU lifetimes must be cancelled/drained before freeing MEP or peer objects. Sequence-number and defect flags must reflect the latest CCM without racing status dumps. Residence port deletion must clear or retire dependent MEPs.

## Test signals
Test MEP create/delete, invalid instance references, peer add/remove, CCM enable/disable with timeout renewal, RDI toggling, port deletion while CFM exists, and status dumps for unexpected opcode/version/level and peer defect flags.
