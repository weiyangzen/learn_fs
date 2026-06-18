<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmmpc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmmpc.h

## Purpose
Defines the ATM MPOA Client daemon ABI for shortcut setup, ingress/egress cache control, MPOA parameter exchange, and control/data socket roles.

## Important APIs, Types, And Functions
`ATMMPC_CTRL` and `ATMMPC_DATA` register sockets. `atmmpc_ioc` selects MPC ingress/egress attachment. `in_ctrl_info`, `eg_ctrl_info`, `mpc_parameters`, `k_message`, and `llc_snap_hdr` carry MPOA protocol data. Numerous `SND_*`, `MPOA_*`, and configuration constants define daemon/kernel message types and defaults.

## Control Flow
The daemon receives kernel trigger messages, sends MPOA resolution requests/replies, opens ingress shortcuts, purges caches, reacts to MPS death, and updates MPC parameters. Kernel and daemon exchange `k_message` records over control sockets.

## State And Persistence
State includes ingress/egress MPOA caches, shortcut VCCs, control ATM addresses, retry/holding timers, parameters, and socket role attachments. It is runtime network state.

## Dependencies And Integration Points
Depends on ATM API/core/types and ATM ioctl ranges. Integrates with MPOA daemons, NHRP/MPOA signaling, and ATM QoS.

## Risks And Edge Cases
Message type coordination, fixed 256-byte DLL header, network-byte-order IP fields, cache id/tag lifetime, timer defaults, and daemon reload/exit handling are fragile.

## Test Signals
Control/data socket registration, ingress/egress cache update/purge, shortcut open flow, parameter reload, MPS death handling, and malformed message rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmmpc.h -->
