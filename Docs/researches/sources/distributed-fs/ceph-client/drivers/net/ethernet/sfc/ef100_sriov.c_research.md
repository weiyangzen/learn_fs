# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_sriov.c

Purpose: Provides EF100 PCI SR-IOV enable/disable plumbing and representor creation for MAE-capable EF100 PFs.

Important APIs and functions: `efx_ef100_sriov_configure()` is the PF `sriov_configure` callback. `efx_ef100_pci_sriov_disable()` disables VFs and tears down VF representors. Static `efx_ef100_pci_sriov_enable()` sets `efx->vf_count`, calls `pci_enable_sriov()`, and creates one VF representor per VF when `nic_data->grp_mae` is present.

Control flow: Enabling stores the requested VF count, enables PCI SR-IOV, returns immediately when MAE groups are absent, otherwise creates representors in order. If any representor creation fails, it destroys all created reps, disables SR-IOV, logs a probe error, clears `vf_count`, and returns the failure. Disabling refuses assigned VFs unless forced, finalizes representors, disables PCI SR-IOV when no VFs are assigned, and returns success.

State and persistence: Mutates `efx->vf_count` and the `efx->vf_reps` list through representor helpers. PCI SR-IOV state persists in the PCI core until disabled. Representor netdev state is runtime-only and must be reconciled on failure.

Dependencies and integration points: Depends on `ef100_nic.h` for EF100 private data, `ef100_rep.h` for representor lifecycle, PCI SR-IOV core APIs, and the generic `efx.c` `sriov_configure` dispatch. It complements EF100 RX/TX mport and representor paths.

Risks: Assigned VFs prevent normal disable. A partial enable must destroy all representors to avoid stale netdevs. The function does not clear `vf_count` on successful disable, relying on broader lifecycle assumptions. Representor behavior exists only when MAE grouping is available.

Test signals: Enable zero and nonzero VF counts, force and non-force disable with assigned VFs, inject representor creation failure, verify representor list cleanup, and validate PCI SR-IOV state after error unwinds.
