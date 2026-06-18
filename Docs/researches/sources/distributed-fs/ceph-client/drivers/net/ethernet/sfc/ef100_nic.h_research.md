<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_nic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_nic.h

## Purpose
Defines EF100 NIC-level public contracts: PF/VF NIC type exports, probe/remove helpers, statistics indices, private NIC data layout, capability-testing macro, and MCDI-facing helper prototypes.

## Important APIs, Types, And Functions
- `extern const struct efx_nic_type ef100_pf_nic_type` and `ef100_vf_nic_type`.
- `enum { EF100_STAT_* }` extends generic stats with EF100 MAC counters.
- `struct ef100_nic_data` is the central EF100 private state object.
- `efx_ef100_has_cap(caps, flag)` maps MCDI capability names to bit tests.
- Prototypes include `efx_ef100_init_datapath_caps()`, `ef100_phy_probe()`, `ef100_filter_table_probe()`, `ef100_get_mac_address()`, and `efx_ef100_lookup_client_id()`.

## Control Flow
No executable control flow exists. The header shapes how `ef100_nic.c`, `ef100_netdev.c`, SR-IOV, TC/MAE, and representor files share EF100 runtime state and invoke NIC-level services.

## State And Persistence
`struct ef100_nic_data` persists for the lifetime of a probed EF100 NIC. It stores firmware capability masks, the MCDI buffer, warm boot count, PF index, event queue phases, stats, port and mport identities, MAE privilege/local interface discovery flags, and hardware TSO limits.

## Dependencies And Integration Points
Includes common SFC `net_driver.h` and `nic_common.h`. It is the integration contract for EF100 PCI, netdev, SR-IOV, MAE/TC, representor, RX/TX, and ethtool code that need NIC type tables or private EF100 state.

## Risks And Edge Cases
Fields in `ef100_nic_data` are consumed across multiple files; initialization order matters. For example TSO limits must be populated before netdev TSO max setters, and MAE flags must be valid before notifier/representor code acts on them. Capability macro correctness depends on MCDI field naming staying aligned with `mcdi_pcol.h`.

## Test Signals
Compile-time checks catch enum/prototype mismatch. Runtime signals include valid stats names/counts, correct TSO limits on netdev, mport/MAE feature behavior, PF/VF type dispatch, and successful MCDI capability/mac/client helper calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_nic.h -->
