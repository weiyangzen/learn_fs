# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm7150.c

## Purpose
Defines the Qualcomm SM7150 TLMM pin controller data for the shared MSM pinctrl driver. It describes three TLMM register tiles (`north`, `south`, `west`), 127 pin descriptors, 120 GPIO-capable pins, 109 mux functions, per-pin groups, SD/UFS special pads, PDC wake mappings, and the `qcom,sm7150-tlmm` platform binding.

## Important APIs, Types, and Functions
The central object is `sm7150_tlmm`, a `struct msm_pinctrl_soc_data` containing pin, function, group, tile, wake IRQ, and errata metadata. `PINGROUP(id, tile, ...)` fills `struct msm_pingroup` entries with tile selection and the standard Qualcomm TLMM register bits: mux at bit 2, pull at bit 0, drive at bit 6, output enable at bit 9, interrupt target at bit 5, raw status at bit 4, and two-bit detection at bit 2. `SDC_QDSD_PINGROUP()` models SDC1/SDC2 pads in a tile-aware way, and `UFS_RESET()` models the UFS reset output on the west tile. `sm7150_pdc_map[]` connects selected GPIOs to PDC wake interrupt IDs. The driver also attaches `.pm = &msm_pinctrl_dev_pm_ops`.

## Control Flow
`sm7150_tlmm_init()` registers a platform driver at `arch_initcall` time. Device-tree matching on `qcom,sm7150-tlmm` calls `sm7150_tlmm_probe()`, which hands the static SoC data to `msm_pinctrl_probe()`. From that point, pin muxing, pin configuration, GPIO operations, IRQ handling, and PM callbacks are all handled by the shared `pinctrl-msm` core using the tables from this file.

## State and Persistence Behavior
The SM7150-specific tables are immutable kernel data. Runtime pin states are not cached here; they are represented by hardware register contents and common-core objects allocated during probe. The tile array affects how the common core maps group register offsets to the correct MMIO resource. `.wakeirq_dual_edge_errata = true` tells the shared core to use its workaround path for dual-edge wake IRQ handling on this SoC.

## Dependencies and Integration Points
Uses Linux module, OF, platform-device, and pinctrl headers plus `pinctrl-msm.h`. It integrates with device tree through `qcom,sm7150-tlmm`, with PM through `msm_pinctrl_dev_pm_ops`, with the PDC interrupt controller through `sm7150_pdc_map[]`, and with consumers through named pin functions such as QUP, CCI, camera MCLK, MDP/EDP sync, TSIF, QDSS, UIM, MI2S, PCIe, USB PHY, WLAN ADC, SD card, and UFS reset.

## Risks
Tile assignment is a major risk: the same per-pin offset can refer to different MMIO windows depending on `NORTH`, `SOUTH`, or `WEST`. `ngpios = 120` deliberately excludes UFS and SDC special pads at descriptors 119-126 from ordinary GPIO use. Wake IRQ behavior depends on both the PDC map and the dual-edge errata flag, so regressions may appear only in suspend/resume or edge-triggered wake tests. Consumer-visible function names must match device-tree bindings exactly.

## Test Signals
Boot on SM7150 hardware or DT emulation and check `qcom,sm7150-tlmm` probe, debugfs pin/function/group registration, GPIO request/configuration for pins below 120, SDC1/SDC2 and UFS reset operation, tile-specific mux writes on north/south/west groups, PDC wake from suspend on mapped GPIOs, dual-edge wake IRQ behavior, and suspend/resume with `msm_pinctrl_dev_pm_ops` active.
