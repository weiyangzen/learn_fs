<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/workarounds.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/workarounds.h

## Purpose
Centralizes hardware workaround predicates and bug-number macros for Siena/Falcon-architecture and EF10-era Solarflare NICs.

## Important APIs, Types, And Functions
- Family predicates: `EFX_WORKAROUND_SIENA(efx)`, `EFX_WORKAROUND_EF10(efx)`, and unconditional `EFX_WORKAROUND_10G(efx)`.
- Bug workarounds: `EFX_WORKAROUND_7884`, `EFX_WORKAROUND_17213`, and `EFX_EF10_WORKAROUND_61265(efx)`.

## Control Flow
No functions run here. Call sites use the macros to conditionally route around hardware/firmware issues based on NIC revision or EF10 private data.

## State And Persistence Behavior
Stateless except for reading NIC revision or EF10 private workaround flags. No persistent behavior is introduced.

## Dependencies And Integration Points
Included by Siena self-test, TX, core NIC code, and other hardware-control paths. It depends on `efx_nic_rev()` and revision constants; the EF10 macro assumes `efx->nic_data` is `struct efx_ef10_nic_data`.

## Risks And Test Signals
The EF10-specific macro is unsafe if used on non-EF10 NIC data. Workaround predicates must match hardware revisions exactly. Test signals are revision-specific behavior in affected paths, especially legacy interrupt storm mitigation and moderation timer access routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/workarounds.h -->
