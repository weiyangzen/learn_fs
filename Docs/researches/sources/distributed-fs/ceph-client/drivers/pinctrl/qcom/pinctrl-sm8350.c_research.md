# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8350.c

## Purpose
Provides the Qualcomm SM8350 TLMM pinctrl SoC table for the shared MSM pinctrl driver. It enumerates 207 pin descriptors, 204 GPIO-capable lines, 134 mux functions, 207 normal/special groups, SDC2 and UFS reset pads, wake IRQ mappings, and the `qcom,sm8350-tlmm` platform driver binding.

## Important APIs, Types, and Functions
The central data object is `sm8350_tlmm`, a `struct msm_pinctrl_soc_data`. `PINGROUP()` describes standard GPIO groups with mux, pull, drive, output, input, and interrupt bit positions at 0x1000-byte per-pin spacing. `SDC_PINGROUP()` describes SDC2 pads with only pull/drive fields. `UFS_RESET()` describes the UFS reset output register. `sm8350_pdc_map[]` maps selected GPIOs to PDC wake interrupt IDs. Probe is a thin wrapper around `msm_pinctrl_probe(pdev, &sm8350_tlmm)`.

## Control Flow
`sm8350_tlmm_init()` registers the platform driver with `arch_initcall()`. A matching device-tree node with compatible `qcom,sm8350-tlmm` invokes `sm8350_tlmm_probe()`. The shared MSM core then registers the pinctrl provider, GPIO chip for `ngpios = 204`, and wake IRQ support from the static tables. Module exit unregisters the platform driver.

## State and Persistence Behavior
This file has no mutable runtime state beyond platform-driver registration. Pin configuration, mux state, and interrupt state persist in hardware registers and common-core data structures. Pins 203-206 are special descriptors for UFS reset and SDC2 and are outside the ordinary GPIO range. The table has no tile array, so offsets are interpreted in a single register namespace by the common core.

## Dependencies and Integration Points
Depends on Linux module, OF, platform-device support and `pinctrl-msm.h`. Integrates with pinctrl/gpiolib/IRQ users through the common Qualcomm core. Device-tree consumers use function and group names for QUP, PCIe clock request, camera, CCI, display, QDSS, audio/MI2S/LPASS slimbus, UIM, MSS/QLINK/coexistence, navigation GPIOs, USB PHY, SDC2, and UFS reset.

## Risks
SM8350 has the largest table in this work item, so off-by-one descriptor/group/function errors are the primary risk. `.ngpios = 204` must remain aligned with pin descriptors and special groups. Wake IRQ map entries are numerous and hardware-specific; bad entries mainly surface in low-power wake tests. The absence of tile metadata means adding tile-style offsets later would require coordinated changes with resource mapping in the common core.

## Test Signals
Build and boot with `qcom,sm8350-tlmm`, verify debugfs shows 207 pins and all functions, request GPIOs below 204, reject or avoid ordinary GPIO use for UFS/SDC special pads, exercise representative QUP, PCIe, camera, CCI, audio, UIM, QDSS, USB, MSS, SDC2, and UFS reset pinctrl states, and validate suspend wake for mapped PDC GPIOs.
