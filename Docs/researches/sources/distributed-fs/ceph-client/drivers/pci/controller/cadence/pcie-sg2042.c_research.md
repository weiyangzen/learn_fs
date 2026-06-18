<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-sg2042.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-sg2042.c

Purpose: Sophgo SG2042 Cadence PCIe host driver. It supplies SG2042-specific config access ops for 4-byte aligned root-port access, disables broken ASPM L0s/L1 advertisement, initializes PHYs, and delegates host setup to classic Cadence code.

Important APIs/types/functions: `sg2042_pcie_root_ops`, `sg2042_pcie_child_ops`, `sg2042_pcie_probe()`, `sg2042_pcie_remove()`, `sg2042_pcie_suspend_noirq()`, `sg2042_pcie_resume_noirq()`, and `sg2042_pcie_pm_ops`.

Control flow: probe allocates a host bridge, installs 32-bit config read/write ops for root bus and generic ops for child buses, sets ASPM quirks, initializes runtime PM without callbacks, initializes PHYs, then calls `cdns_pcie_host_setup()`. Remove disables the Cadence host and PHYs. PM noirq suspend/resume cycles PHY power only.

State/persistence: runtime state is primarily `struct cdns_pcie` embedded in `struct cdns_pcie_rc`, stored as platform drvdata. Hardware state includes PHY power, root-port config and address translations from common Cadence host setup, and ASPM link capability masking.

Dependencies/integration: platform resources consumed by common Cadence host setup, generic PHY framework, runtime PM helper wrappers, and DT compatible `sophgo,sg2042-pcie-host`.

Risks: the root/child config ops split is essential because root-port byte/word config access is not supported. Any future bridge ops override must preserve `child_ops`. Suspend/resume does not reinitialize host translations, so it assumes PHY cycling is sufficient or higher layers preserve controller state.

Test signals: SG2042 root config reads/writes using 32-bit ops, child config byte/word/dword accesses, ASPM disabled in LNKCAP, PHY init and PM resume, host remove cleanup, and enumeration behind bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-sg2042.c -->
