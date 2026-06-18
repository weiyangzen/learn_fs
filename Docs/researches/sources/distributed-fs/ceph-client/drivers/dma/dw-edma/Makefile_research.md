## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/Makefile

Purpose: Kbuild rules for the DesignWare eDMA core, versioned register implementations, optional debugfs files, and PCIe glue.

Important APIs/types/functions: links `dw-edma-core.o`, `dw-edma-v0-core.o`, and `dw-hdma-v0-core.o` into `dw-edma.o`; conditionally adds v0 and HDMA debugfs objects under `CONFIG_DEBUG_FS`; builds `dw-edma-pcie.o` under `CONFIG_DW_EDMA_PCIE`.

Control flow: object composition determines which implementation files are linked into the core module and whether debugfs entry points are present.

State and persistence: no runtime state.

Dependencies and integration: mirrors the `dw_edma_core_ops` dispatch architecture: common core plus eDMA v0 and HDMA v0 register back ends.

Risks and test signals: missing debugfs object linkage would break debug builds; missing core objects would break symbol resolution for `dw_edma_probe()`. Test by building with and without `CONFIG_DEBUG_FS` and with PCIe glue enabled.
