# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-pltfm.h

Purpose: declares the shared platform wrapper API for DesignWare MMC platform drivers and exposes the common DW MMC PM operations.

Important APIs and types: declarations are `dw_mci_pltfm_register(struct platform_device *pdev, const struct dw_mci_drv_data *drv_data)`, `dw_mci_pltfm_remove(struct platform_device *pdev)`, and `dw_mci_pmops`.

Control flow: SoC-specific platform drivers include this header, pass their optional `dw_mci_drv_data` to registration during probe, use `dw_mci_pltfm_remove` during remove, and reference `dw_mci_pmops` or variant PM wrappers in their driver structs.

State and persistence: the header owns no state. All state is allocated in `dw_mci_alloc_host` and held in `struct dw_mci`.

Dependencies and integration points: depends on visible declarations of `struct platform_device`, `struct dw_mci_drv_data`, and `struct dev_pm_ops` from included source context. It is the boundary between generic platform glue and SoC-specific DW MMC adapters.

Risks: it uses `extern` declarations only and does not include the defining headers itself, so include order matters. PM ops are shared across many adapters; variant drivers must choose custom wrappers when they need extra resume/suspend behavior.

Test signals: compile coverage across all DW MMC platform extension drivers and module load/unload tests through `dw_mci_pltfm_register/remove`.
