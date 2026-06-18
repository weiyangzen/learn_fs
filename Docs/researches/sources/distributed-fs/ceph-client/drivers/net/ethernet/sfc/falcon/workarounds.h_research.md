<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/workarounds.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/workarounds.h

## Purpose
Centralizes Falcon EF4 hardware workaround predicates, keyed by NIC revision or general 10G capability, so RX/TX/NIC code can gate erratum-specific behavior.

## Important APIs, types, and functions
- Revision predicates: `EF4_WORKAROUND_FALCON_A`, `EF4_WORKAROUND_FALCON_AB`, and `EF4_WORKAROUND_10G`.
- Named workaround macros include bug IDs 7884, 15592, 5129, 5391, 5583, 5676, 6555, 7244, 7803, and 8071.

## Control flow
No control flow is implemented here. Callers expand macros to conditional logic based on `ef4_nic_rev(efx)`.

## State and persistence behavior
No state is stored. Workaround decisions are derived from the NIC revision at runtime.

## Dependencies and integration points
Used by Falcon RX and TX paths and likely NIC-specific code to handle descriptor sizing, overlength RX recovery, TX minimum size, flush behavior, and other errata.

## Risks and test signals
Risk is incorrect revision gating, which can either miss required erratum handling or apply legacy behavior to newer chips. Test signals are hardware-revision-specific RX/TX stress tests, flush/reset tests, overlength RX handling, and descriptor alignment/page-boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/workarounds.h -->
