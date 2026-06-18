# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom-common.h

Purpose: This header declares the shared Qualcomm PCIe helper API for equalization and 16 GT/s lane margining.

Important APIs, types, and functions: It forward-declares `struct dw_pcie` and declares `qcom_pcie_common_set_equalization()` and `qcom_pcie_common_set_16gt_lane_margining()`.

Control flow: The header has no execution. Including drivers call the declared helpers during link setup when DBI registers are accessible and before link training or speed-dependent capability exposure is finalized.

State and persistence behavior: No state is declared in the header. Hardware effects are in the corresponding C implementation.

Dependencies and integration points: Used by Qualcomm root-complex and endpoint drivers alongside `pcie-designware.h`. The forward declaration keeps include coupling small while preserving type checking for function parameters.

Risks: Prototype drift from `pcie-qcom-common.c` would break builds for both Qualcomm drivers. Adding helper declarations here makes them part of the internal Qualcomm DWC glue API and should preserve DBI availability assumptions.

Test signals: Build `pcie-qcom.c`, `pcie-qcom-ep.c`, and `pcie-qcom-common.c` together and as modules/built-ins under relevant Kconfig combinations to catch missing prototypes or export mismatches.
