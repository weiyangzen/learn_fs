# sources/distributed-fs/ceph-client/include/soc/rockchip/rk3399_grf.h

Purpose: defines RK3399 PMU GRF register offset and bit masks for DDR type and channel bus-width discovery.

Important APIs/types/functions: provides `RK3399_PMUGRF_OS_REG2`, `RK3399_PMUGRF_OS_REG2_DDRTYPE`, `RK3399_PMUGRF_OS_REG2_BW_CH0`, and `RK3399_PMUGRF_OS_REG2_BW_CH1`.

Control flow: consumers read PMU GRF OS_REG2 through regmap and extract memory type/channel width using the masks.

State and persistence: values are bootloader/firmware-populated GRF state describing DRAM configuration. The header has no mutable state.

Dependencies and integration: relies on `GENMASK()` via includers and is used by Rockchip DFI/devfreq/DMC code along with `rockchip_grf.h`.

Risks: wrong masks misidentify memory topology, leading to bad bandwidth or devfreq calculations. Test signals include RK3399 DMC/devfreq probe, DFI event reporting, and sysfs/devfreq bandwidth sanity checks.
