# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8150.c

## Purpose
Supplies the Qualcomm SM8150 pinctrl/TLMM SoC description for the MSM pinctrl core. It defines four tiles (`north`, `south`, `east`, `west`), 179 pin descriptors, 176 GPIO-capable pins, 128 mux functions, 179 normal/special groups, SDC2 and UFS reset special pads, PDC wake mappings, and the platform driver for compatible `qcom,sm8150-pinctrl`.

## Important APIs, Types, and Functions
`sm8150_pinctrl` is the main `struct msm_pinctrl_soc_data`. `PINGROUP()` constructs tile-aware GPIO groups with standard Qualcomm TLMM field positions and ten mux entries per group including GPIO mode. `SDC_QDSD_PINGROUP()` describes SDC2 pads on the north tile with only pull/drive fields. `UFS_RESET()` describes the UFS reset output on the south tile. `sm8150_pdc_map[]` maps selected GPIOs to PDC wake IRQ IDs and includes some GPIOs with multiple wake IDs. `sm8150_pinctrl_probe()` calls `msm_pinctrl_probe()` and registration occurs via `arch_initcall()`.

## Control Flow
The module registers the platform driver early in boot. When the OF core matches `qcom,sm8150-pinctrl`, probe passes `sm8150_pinctrl` into the common MSM implementation. The common code then interprets the tile names, group offsets, bit fields, and wake map to serve pinctrl, pinconf, GPIO, and IRQ requests. No custom SM8150 runtime code executes beyond probe/register/unregister.

## State and Persistence Behavior
SM8150-specific data is static. Register state is held in TLMM hardware and manipulated by the shared core when clients select states or configure GPIOs. `.wakeirq_dual_edge_errata = true` persists as SoC metadata used by the common interrupt wake path. `.ngpios = 176` means pins 175-178 are descriptors/groups for UFS reset and SDC2, not general GPIO lines.

## Dependencies and Integration Points
Depends on `pinctrl-msm.h`, Linux OF/platform driver support, pinctrl, gpiolib, and irqchip wake infrastructure via the common core. Integration points include device-tree pinctrl states for QUP, QSPI, TSIF, RGMII/EMAC, PCIe, UIM, MI2S/audio, LPASS slimbus, camera/display, QDSS, SD write/SDC4 functions, USB PHY, SDC2, UFS reset, and PDC wake sources.

## Risks
The four-tile layout makes incorrect tile assignment especially damaging because register offsets are otherwise uniform. The PDC map has duplicate GPIO entries for some pins, so consumers and wake logic need coverage for all intended wake routes. The special SDC/UFS groups use `-1` for unsupported mux/IRQ fields, and they are excluded from `ngpios`; treating them as GPIOs would cause invalid register operations. Because this file is almost entirely static arrays, off-by-one errors in pin descriptors, group indices, or function enum ordering can compile cleanly but misprogram hardware.

## Test Signals
Useful signals include successful probe for `qcom,sm8150-pinctrl`, debugfs enumeration of all tiles/groups/functions, representative mux selection in each tile, GPIO input/output/pull/drive on pins below 176, SDC2 and UFS reset behavior, PDC wake from suspend including duplicated wake-map GPIOs, dual-edge wake IRQ handling, and peripheral bring-up for QUP, QSPI, PCIe, UIM, audio, camera, display, and Ethernet-related pin states.
