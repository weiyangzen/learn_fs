# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi_cna.h

## Purpose
`bfi_cna.h` defines firmware mailbox message formats for converged network adapter functions outside the main ENET queue setup path: generic physical port enable/disable/statistics messages and CEE/DCBX/LLDP configuration and statistics messages.

## Important APIs, Types, and Functions
- `enum bfi_port_h2i` and `enum bfi_port_i2h` define port enable, disable, get-stats, and clear-stats opcodes.
- `struct bfi_port_generic_req` and `struct bfi_port_generic_rsp` provide message-tagged request/response layouts for enable/disable/clear style operations.
- `struct bfi_port_get_stats_req` carries a DMA address for port statistics retrieval.
- `union bfi_port_h2i_msg_u` and `union bfi_port_i2h_msg_u` group all port mailbox payloads by direction.
- `enum bfi_cee_h2i_msgs` and `enum bfi_cee_i2h_msgs` define CEE get-config, reset-stats, and get-stats opcodes.
- `struct bfi_cee_get_req`, `struct bfi_cee_get_rsp`, `struct bfi_cee_stats_req`, and `struct bfi_cee_stats_rsp` carry CEE DMA requests and completion status.
- `union bfi_cee_h2i_msg_u` and `union bfi_cee_i2h_msg_u` group CEE payloads.

## Control Flow and State
The file is ABI-only. Runtime users allocate DMA buffers for stats or configuration, fill a `bfi_mhdr`, and send class-specific mailbox messages through IOC mailbox plumbing. Responses carry command status and route back through registered mailbox handlers. The CEE attach and memory claim calls in `bna_ioceth_init()` indicate that CEE uses these formats as a common module attached to the same IOC.

## State and Persistence Behavior
No state is stored in this header. The structs describe transient mailbox messages and firmware-DMA exchanges. Persistent effects occur in firmware or device configuration: port enable/disable state, cleared counters, and fetched CEE/LLDP configuration/statistics.

## Dependencies and Integration Points
The header includes `bfi.h` for common message headers/address types and `bfa_defs_cna.h` for CNA-specific definitions. In this group, its strongest integration point is `bna_ioceth_init()`, which attaches `bfa_nw_cee` and claims DMA memory before MSGQ. The port message class is related to but distinct from the ENET port admin-up path in `bfi_enet.h`.

## Risks
- The file contains two reset-stats structs (`bfi_lldp_reset_stats` and `bfi_cee_reset_stats`) with identical layouts and comments, which can invite confusion at call sites.
- DMA address requests require correct endian/address packing by callers.
- Command status is only an 8-bit field; callers must translate firmware statuses carefully.
- The unions are packed ABI contracts and should not be reordered casually.

## Test Signals
Signals include successful CEE attach and configuration retrieval, CEE statistics DMA completion, reset-stats completion, physical port stat retrieval, and no mailbox class/opcode mismatch when CEE and port modules are enabled with the IOC.
