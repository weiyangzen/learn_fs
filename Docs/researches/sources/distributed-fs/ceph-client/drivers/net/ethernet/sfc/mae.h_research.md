<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae.h

## Purpose
Declares the EF100 MAE driver interface used by TC offload, counter streaming, mport management, conntrack offload, and MAE lifecycle code.

## Important APIs, types, and functions
- Public mport APIs and `struct mae_mport_desc`, including net-port, alias, and VNIC descriptors plus rhashtable linkage and devlink port storage.
- `struct efx_mae` owns the NIC pointer and mport rhashtable.
- Counter stream APIs, table/capability APIs, match capability validators, counter resource APIs, encap metadata APIs, pedit MAC APIs, action set/list APIs, encap match APIs, LHS rule APIs, CT APIs, action rule APIs, and lifecycle APIs.
- `struct mae_caps` stores match field count, supported encap types, action priorities, and per-field AR/OR support arrays.

## Control flow
The header has no executable flow. It defines the call graph boundary between TC/offload code and the MAE MCDI implementation in `mae.c`.

## State and persistence behavior
Types declared here describe in-memory MAE state and firmware-backed resource identifiers. Runtime ownership is implemented in `mae.c`; the header itself does not allocate or free state.

## Dependencies and integration points
Includes devlink, core net driver definitions, TC definitions, and `mcdi_pcol.h` for firmware NULL constants. It is consumed by EF100 NIC initialization, TC offload, conntrack, counter RX, and cleanup paths.

## Risks and test signals
The header contains two declarations named `efx_mae_lookup_mport` with identical C types but different parameter names/semantics (`selector` near the top and `vf` near the bottom), while `mae.c` separately implements `efx_mae_fw_lookup_mport` for selector lookup. This is legal but confusing and is a contract-drift risk. Test signals are build coverage, sparse/prototype checks, MAE init/enumeration, VF mport lookup, and TC offload resource operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae.h -->
