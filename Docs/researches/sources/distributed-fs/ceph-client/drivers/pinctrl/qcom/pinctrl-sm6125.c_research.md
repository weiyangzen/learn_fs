# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6125.c

## Purpose
Provides the SM6125 TLMM SoC description for the MSM pinctrl core. It is a tiled controller with 133 regular GPIOs, UFS reset, SDC1/SDC2 pad groups, a large mux matrix spanning QUP, camera, audio, display, USB, navigation, UIM, QDSS, and test functions, plus MPM wake routing.

## Important APIs, Types, And Functions
`sm6125_tiles[]` names `south`, `east`, and `west` MMIO tiles. `PINGROUP()` creates tiled GPIO descriptors using a 0x1000 per-pin stride and standard TLMM bit assignments. `SDC_QDSD_PINGROUP()` and `UFS_RESET()` encode special pad/reset groups with limited capabilities and tile metadata. `sm6125_pins[]`, `enum sm6125_functions`, function group arrays, `sm6125_functions[]`, and `sm6125_groups[]` define the pinctrl ABI. `sm6125_mpm_map[]` maps GPIOs to MPM wake lines. `sm6125_tlmm` sets `ngpios = 134`.

## Control Flow
The driver is registered early through `arch_initcall`. A `qcom,sm6125-tlmm` platform device calls `sm6125_tlmm_probe()`, which passes the static data to `msm_pinctrl_probe()`. The common driver maps tiles, registers pinctrl/gpio/irq support, resolves device-tree group/function strings, and applies mux and pinconf settings. Suspend wake setup uses the MPM map.

## State And Persistence
There is no local runtime state. Hardware configuration persists in TLMM, UFS, and SDC registers after the common driver writes them. GPIO0-132 plus UFS reset at group 133 are counted in `ngpios`; SDC groups 134-140 are special pinctrl-only pads.

## Dependencies And Integration Points
Depends on `pinctrl-msm` tiled controller support and MPM wake routing. Integrates with QUP00-04 and QUP10-14 serial engines, camera CCI/MCLK/timers, WSA/MI2S/SoundWire/audio reference pins, DisplayPort/eDP hotplug and LCD, USB PHY/test pins, navigation/GPS, UIM, QLINK, QDSS, DDR/test hooks, and storage controllers.

## Risks
This is one of the denser tables in the set; selector order and tile assignment are the central correctness risks. Some functions are named `unused1`/`unused2`, which may indicate reserved hardware modes that should not be exposed to board files unless bindings deliberately allow them. MPM mappings include noncontiguous GPIOs and low wake numbers; wrong entries can be hard to diagnose because normal GPIO interrupts may still work while wake from suspend fails. SDC2 uses a high offset `0x58b000`, so resource sizing must cover it.

## Test Signals
Boot probe, debugfs inspection for all functions, GPIO/IRQ tests across south/east/west tiles, suspend wake using representative MPM-mapped GPIOs, UFS reset and SD1/SD2 operation, QUP buses, camera and display pin states, audio interfaces, USB/eDP/DP hotplug pins, and checks that reserved/unused muxes are not selected by production DT. Source size reviewed: 1282 lines.
