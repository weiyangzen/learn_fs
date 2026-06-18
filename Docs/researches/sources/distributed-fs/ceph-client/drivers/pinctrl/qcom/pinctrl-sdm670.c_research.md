# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm670.c

## Purpose

`pinctrl-sdm670.c` is the Qualcomm SDM670 TLMM pinctrl/GPIO driver data source for the shared MSM pinctrl core. It describes the SDM670 TLMM register layout, pin descriptors, alternate functions, dummy/uncontrolled groups, UFS and SDC groups, reserved GPIOs, PDC wake mapping, and driver binding. The source has a simple platform probe wrapper but important table-level hardware policy.

## Important APIs, Types, and Data

- Includes `pinctrl-msm.h` and provides `sdm670_pinctrl`, a `struct msm_pinctrl_soc_data`.
- Base constants `NORTH`, `SOUTH`, and `WEST` are absolute TLMM tile offsets folded directly into each group register address rather than represented as named tile resources.
- `PINGROUP()` creates normal GPIO groups with ten mux slots and standard TLMM mux/config/IRQ bit positions.
- `PINGROUP_DUMMY()` defines pin groups that have no controllable registers or alternate functions; all control bits are set to `-1`.
- `SDC_QDSD_PINGROUP()` and `UFS_RESET()` define special storage-related groups with limited capabilities.
- `sdm670_pins[]`, `DECLARE_MSM_GPIO_PINS()`, per-function group arrays, `enum sdm670_functions`, `sdm670_functions[]`, and `sdm670_groups[]` provide the pinctrl database.
- Function coverage includes QUP, camera/CCI, MDP/eDP, TSIF, PCIe, USB PHY/test, UIM, LPASS/MI2S/SLIMbus/audio, QDSS, DDR/test, WLAN ADC, GPS/navigation, and modem-related signals.
- `sdm670_reserved_gpios[]` reserves GPIOs 58-64, 69-74, and 104, terminated by `-1`.
- `sdm670_pdc_map[]` maps GPIO lines to PDC wake IRQs.
- `sdm670_pinctrl` sets `.ngpios = 151`, reserved GPIOs, wake map, and `.wakeirq_dual_edge_errata = true`.
- OF matching binds `qcom,sdm670-tlmm`.

## Control Flow

The driver registers at `arch_initcall()` and unregisters at module exit. OF matching creates the platform device, and `sdm670_pinctrl_probe()` delegates directly to `msm_pinctrl_probe(pdev, &sdm670_pinctrl)`. The shared MSM core maps registers, registers pinctrl/GPIO/IRQ providers, applies reserved GPIO policy, and uses the wake map and dual-edge errata flag for interrupt behavior.

## State and Persistence

There is no mutable local state. Static tables define the hardware model. Runtime state belongs to the MSM core, and TLMM register values persist in hardware. Reserved GPIOs constrain gpiolib exposure/usage through the core. Dummy groups intentionally represent pins that cannot be controlled by this driver.

## Dependencies and Integration Points

The file depends on Linux platform/OF/module infrastructure and the Qualcomm MSM pinctrl core. It integrates with SDM670 device trees, pinctrl clients, gpiolib, and PDC wake interrupt support. The reserved GPIO list and dummy groups are important integration boundaries with firmware or inaccessible hardware.

## Risks and Edge Cases

- Absolute base offsets are embedded in every group; a base constant error affects an entire tile's register accesses.
- Dummy groups must remain nonfunctional. Accidentally adding control bits could cause writes to offset zero or unrelated registers.
- Reserved GPIO handling is required to avoid exposing firmware-owned or unavailable lines.
- Dual-edge wake errata handling changes interrupt programming; omitting or misusing the flag can produce missed or repeated wake events.
- `.ngpios = 151` excludes special groups after the GPIO range; changing this can expose UFS/SDC descriptors as normal GPIOs.
- Wake map validation requires suspend/resume hardware testing and will not be proven by compile coverage.

## Test Signals

Useful signals include compile success, successful probe for `qcom,sdm670-tlmm`, expected GPIO count with reserved GPIOs unavailable, debugfs confirmation of dummy/special groups, pinctrl state application for QUP/camera/display/audio/storage consumers, GPIO IRQ tests including dual-edge cases, and suspend/resume wake tests for GPIOs listed in `sdm670_pdc_map[]`.
