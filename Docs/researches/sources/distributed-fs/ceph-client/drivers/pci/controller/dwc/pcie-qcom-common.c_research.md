# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom-common.c

Purpose: This file provides shared Qualcomm DesignWare PCIe tuning helpers used by Qualcomm RC and EP drivers. It programs DWC Gen3+ equalization settings and Gen4 16 GT/s lane-margining capability registers.

Important APIs, types, and functions: `qcom_pcie_common_set_equalization()` iterates from 8.0 GT/s to the controller max link speed and programs `GEN3_RELATED_OFF`, `GEN3_EQ_FB_MODE_DIR_CHANGE_OFF`, and `GEN3_EQ_CONTROL_OFF`. `qcom_pcie_common_set_16gt_lane_margining()` programs `GEN4_LANE_MARGINING_1_OFF` and `GEN4_LANE_MARGINING_2_OFF`. Both symbols are exported GPL for use by multiple Qualcomm PCIe modules.

Control flow: Equalization selects a rate shadow for each supported speed, clears noncompliance and EQ fields, sets timing/evaluation/cursor-delta values, and clears phase/control vectors. The loop stops and warns if the derived speed exceeds 32.0 GT/s. Lane margining clears existing max offset/step fields, writes Qualcomm values for voltage and timing, advertises independent error sampler and reporting method, clears unsupported vertical voltage indication, and writes max lanes and sample rates from `pci->num_lanes`.

State and persistence behavior: State is hardware-register state only. The helpers modify DBI registers on the active controller and do not store driver-private state. Their effects are re-applied by RC/EP link bring-up paths.

Dependencies and integration points: Depends on `pcie-designware.h` DWC DBI helpers and register definitions, Linux PCI link speed helpers, and `struct dw_pcie`. Called from `pcie-qcom.c` and `pcie-qcom-ep.c` before enabling LTSSM/link training.

Risks: These helpers write low-level PHY/link training policy across data rates. Incorrect field values can break Gen3/Gen4 link training or margining reporting. The equalization loop depends on `pcie_get_link_speed(pci->max_link_speed)` returning an encoded PCI speed compatible with the loop bounds. Register access assumes DBI is available and writable at the call point.

Test signals: On Qualcomm RC and EP hardware, test Gen3, Gen4, and higher max-speed configurations; confirm link training succeeds at target speeds, no warning occurs for supported speeds, 16 GT/s lane margining registers advertise expected lane counts, and repeated link bring-up reprograms consistent values.
