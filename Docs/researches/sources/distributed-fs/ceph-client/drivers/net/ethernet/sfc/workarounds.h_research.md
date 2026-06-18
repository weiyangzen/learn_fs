# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/workarounds.h

Purpose: centralizes SFC hardware workaround predicates for EF10-era NIC revisions.

Important macros: `EFX_WORKAROUND_EF10()` checks Hunt A0 or newer. `EFX_EF10_WORKAROUND_35388()` and `EFX_WORKAROUND_35388()` gate the event-block register lockup workaround for Hunt A0 when the NIC-data flag is set. `EFX_EF10_WORKAROUND_61265()` exposes the moderation timer MCDI-access workaround flag.

State and dependencies: macros depend on `efx_nic_rev()` and `struct efx_ef10_nic_data` fields populated by NIC probing. There is no state in the header.

Risks and tests: incorrect revision predicates can enable slow paths unnecessarily or skip required hardware safety behavior. Test with NIC-data quirk flags for Hunt A0 and later revisions, especially event queue and interrupt moderation paths.
