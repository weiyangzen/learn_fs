# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6350.c

## Purpose
Defines the SM6350 TLMM controller data for the common MSM pinctrl driver. It covers 156 regular GPIOs, UFS reset, SDC1/SDC2 pads, a broad mux set for QUP, camera, display, LPASS/audio, UIM, QLINK, RFFE, USB/PCIe, QDSS, and test functions, plus PDC wake routing with a dual-edge wake erratum flag.

## Important APIs, Types, And Functions
`PINGROUP()` models normal GPIOs with 0x1000 stride and standard TLMM mux/pull/drive/output/interrupt fields. `SDC_PINGROUP()` and `UFS_RESET()` define special pad/reset groups with limited field support. `sm6350_pins[]`, `enum sm6350_functions`, function group arrays, `sm6350_functions[]`, and `sm6350_groups[]` form the pinctrl ABI. `sm6350_pdc_map[]` maps GPIOs to PDC IRQs. `sm6350_tlmm` sets `ngpios = 157`, wakeirq metadata, and `.wakeirq_dual_edge_errata = true`.

## Control Flow
`sm6350_tlmm_init()` registers the platform driver at `arch_initcall`. The `qcom,sm6350-tlmm` match calls `sm6350_tlmm_probe()`, which delegates to `msm_pinctrl_probe()`. Common code registers pinctrl, pinmux, pinconf, GPIO, and IRQ domains, applies DT-requested pin states, and uses the PDC wake map plus erratum flag when configuring wake-capable interrupts.

## State And Persistence
The file is static data only. Runtime state is in common driver allocations and TLMM/PDC hardware. `ngpios = 157` includes GPIO0-155 plus UFS reset at group 156; SDC groups 157-163 are special pinctrl-only groups. The dual-edge wake erratum changes wakeirq behavior in the common driver but is declared here as a SoC property.

## Dependencies And Integration Points
Depends on `pinctrl-msm` support for wake maps and dual-edge wake errata. Integrates with QUP/I3C, CCI/camera clocks, MDP/eDP/DP, LPASS external/audio/MI2S/SLIMbus/SoundWire-related pads, UIM, RFFE front-end buses, USB PHY, PCIe clock request, QLINK, QDSS, SD/eMMC, UFS, and WLAN/navigation/test interfaces.

## Risks
The table has many high-numbered pins with no mux alternatives, so off-by-one errors around GPIO155/UFS/SDC boundaries are likely audit points. The PDC wake map is large and nonsequential; wrong entries can pass normal IRQ tests while failing wake. `.wakeirq_dual_edge_errata = true` is significant: removing it could break both-edge wake semantics. Several QDSS GPIO aliases and audio functions overlap pins, making board-level mux conflicts possible.

## Test Signals
Probe and debugfs inspection on SM6350, GPIO value/direction and interrupt tests over low/mid/high pins, both-edge wake tests on mapped GPIOs, UFS reset and SD1/SD2 operation, QUP/I3C buses, camera CCI/MCLK, display hotplug/vsync, LPASS/audio pin states, UIM/RFFE/QLINK, USB/PCIe control pins, and verification of wake behavior under the dual-edge erratum path. Source size reviewed: 1389 lines.
