# sources/distributed-fs/ceph-client/include/soc/rockchip/rk3568_grf.h

Purpose: defines RK3568 PMU GRF OS register offsets and masks for DRAM type, channel width, DRAM type v3, and sysreg version.

Important APIs/types/functions: provides `RK3568_PMUGRF_OS_REG2`, `RK3568_PMUGRF_OS_REG2_DRAMTYPE_INFO`, `RK3568_PMUGRF_OS_REG2_BW_CH0`, `RK3568_PMUGRF_OS_REG3`, `RK3568_PMUGRF_OS_REG3_DRAMTYPE_INFO_V3`, and `RK3568_PMUGRF_OS_REG3_SYSREG_VERSION`.

Control flow: DFI/devfreq code reads OS registers, checks sysreg version, and selects old or v3 DRAM-type interpretation.

State and persistence: values are hardware/firmware-populated GRF configuration state. The header has no runtime state.

Dependencies and integration: depends on `GENMASK()` through includers. Used by Rockchip DFI event and memory bandwidth logic.

Risks: version-dependent interpretation can misclassify DRAM if masks are wrong. Test signals include RK3568 DFI probe, memory type reporting, devfreq event counts, and boot logs on boards with different sysreg versions.
