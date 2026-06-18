# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uda.h

## Purpose
This header declares UDA address-handle and multicast management interfaces and defines the software address-handle structures used by the IRDMA SC layer.

## Important APIs, Types, And Functions
- Constants define UDA scaling limits: `IRDMA_UDA_MAX_FSI_MGS`, `IRDMA_UDA_MAX_PFS`, and `IRDMA_UDA_MAX_VFS`.
- `struct irdma_ah_info` contains VSI, PD index, ARP index, source/destination IP addresses, flow label, AH index, VLAN tag, insert-VLAN flag, traffic class/TOS, hop limit/TTL, destination MAC, and validity flags.
- `struct irdma_sc_ah` binds an AH info block to the SC device.
- Function declarations cover AH access and multicast access plus software multicast add/delete.
- Inline wrappers translate create/destroy AH and create/modify/destroy multicast group calls into CQP opcodes.

## Control Flow
Callers initialize `irdma_sc_ah` with `irdma_sc_init_ah()`, fill `irdma_ah_info`, and then call inline create/destroy wrappers that delegate to `irdma_sc_access_ah()`. Multicast callers fill `irdma_mcast_grp_info`, update the software group entries with add/delete helpers, and issue create/modify/destroy through `irdma_access_mcast_grp()`.

## State And Persistence
The header defines no storage. AH state persists in caller-owned `struct irdma_sc_ah` and hardware address-vector table entries. Multicast state persists in `irdma_mcast_grp_info` structures defined elsewhere and in hardware after CQP commands.

## Dependencies And Integration Points
It depends on SC device/VSI and CQP types, multicast group types from other IRDMA headers, and CQP opcode constants. It is included by `type.h`, `uda.c`, and other code that needs AH creation for CM, RoCE UD, multicast, or IEQ handling.

## Risks And Edge Cases
The inline wrappers hide opcode selection but do not validate inputs. `irdma_ah_info` contains both IPv4/IPv6 arrays and validity flags; callers must fill the correct lanes and byte order expected by hardware WQE construction.

## Test Signals
Compile checks should catch signature drift. Runtime signals are successful AH create/destroy CQP completions and multicast group create/modify/destroy flows using the inline wrappers.
