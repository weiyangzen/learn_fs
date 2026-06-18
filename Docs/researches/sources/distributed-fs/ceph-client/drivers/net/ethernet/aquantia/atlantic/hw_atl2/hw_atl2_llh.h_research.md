# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_llh.h

## Purpose
This public low-level ATL2 header declares the A2 register helper functions implemented in `hw_atl2_llh.c`. It separates higher-level ATL2 policy code from raw register addresses and bitfield macros.

## Important APIs, types, and functions
The declarations cover TX interrupt moderation, RSS redirection selection and hash type, new RPF enable, L2 unicast/broadcast filter tags, RSS redirection rows, VLAN filter tags, TX queue-to-TC random mapping, TX buffer clock gating, TX scheduler data arbiter/credit/weight programming, hardware version and launch-time initialization, action resolver record/section programming, firmware shared input/output buffer access, host-finished/MCP-finished handshake bits, MCP boot register access, and host request interrupt get/clear.

## Control flow
The header has no executable control flow. It defines the callable surface that `hw_atl2.c` uses for datapath/filter setup and that `hw_atl2_utils*.c` use for firmware boot/shared-buffer protocol.

## State and persistence
No local state is defined. The declared functions operate on `struct aq_hw_s` and mutate or read device registers and firmware shared buffers.

## Dependencies and integration points
Only `linux/types.h` and a forward declaration of `struct aq_hw_s` are needed, keeping the API lightweight. This file is included by ATL2 implementation files that need hardware access without pulling in the complete internal register map directly.

## Risks
The header exposes low-level functions without parameter range documentation beyond names. Callers must know valid queue, TC, filter, resolver, and shared-buffer ranges from `hw_atl2_internal.h`, `hw_atl2_llh_internal.h`, and firmware ABI structures.

## Test signals
Compile-time coverage ensures declarations match definitions. Runtime coverage comes indirectly through ATL2 init, firmware boot, RSS, VLAN, ART, and interrupt moderation tests.
