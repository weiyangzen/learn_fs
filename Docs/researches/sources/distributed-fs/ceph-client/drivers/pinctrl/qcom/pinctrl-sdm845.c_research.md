# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm845.c

## Purpose

`pinctrl-sdm845.c` is the Qualcomm SDM845 TLMM pinctrl/GPIO data driver for the shared MSM pinctrl core. It describes SDM845 GPIOs, alternate functions, storage special groups, UFS reset, PDC wake interrupt mapping, ACPI-specific reserved GPIO handling, and both DT and ACPI platform binding. Unlike many table-only TLMM files, its probe path explicitly chooses between DT and ACPI SoC data.

## Important APIs, Types, and Data

- Includes `linux/acpi.h` plus the standard module/OF/platform headers and `pinctrl-msm.h`.
- Base constants `NORTH`, `SOUTH`, and `EAST` are absolute register offsets for TLMM regions.
- `PINGROUP()` creates normal `struct msm_pingroup` records with eleven mux slots and standard GPIO/IRQ bit positions.
- `SDC_QDSD_PINGROUP()` describes SDC2 clock/command/data groups with pull/drive support but no mux/GPIO/IRQ behavior.
- `UFS_RESET()` describes the UFS reset pseudo group at fixed registers.
- `sdm845_pins[]`, `DECLARE_MSM_GPIO_PINS()`, `enum sdm845_functions`, function group arrays, `sdm845_functions[]`, and `sdm845_groups[]` define the full pinctrl graph.
- Function coverage includes QUP, CCI/camera, MDP/eDP, TSIF, PCIe, USB PHY/test, UIM, LPASS/MI2S/SLIMbus/audio, QDSS, DDR/test, WLAN ADC, GPS/navigation, modem signals, and other SoC test/debug functions.
- `sdm845_acpi_reserved_gpios[]` reserves GPIOs `0-3` and `81-84` for ACPI systems.
- `sdm845_pdc_map[]` maps GPIO lines to PDC wake IRQs.
- `sdm845_pinctrl` is the DT path with functions, wake map, 151 GPIOs, and `.wakeirq_dual_edge_errata = true`.
- `sdm845_acpi_pinctrl` is the ACPI path with pins/groups, reserved GPIOs, and 150 GPIOs but no function table or wake map.
- ACPI matching uses ID `QCOM0217`; OF matching uses `qcom,sdm845-pinctrl`.
- The platform driver supplies `&msm_pinctrl_dev_pm_ops`, integrating generic suspend/resume handling.

## Control Flow

`sdm845_pinctrl_init()` registers the platform driver at `arch_initcall()`. In `sdm845_pinctrl_probe()`, DT devices call `msm_pinctrl_probe()` with `sdm845_pinctrl`. ACPI devices detected by `has_acpi_companion()` call `msm_pinctrl_probe()` with `sdm845_acpi_pinctrl`. Devices with neither firmware description fail with `-EINVAL` after logging an error. The shared MSM core then owns all pinctrl, GPIO, IRQ, and PM behavior. Exit unregisters the platform driver.

## State and Persistence

The file contains immutable hardware tables only. The generic MSM core owns runtime state and maps TLMM registers. Pin mux/configuration and interrupt settings persist in hardware registers. ACPI operation changes exposed capabilities through a separate SoC-data table rather than modifying the DT table in place.

## Dependencies and Integration Points

The source depends on Linux ACPI, OF, platform driver, module, pinctrl, GPIO, IRQ, and PM infrastructure through the MSM core. It integrates with both `qcom,sdm845-pinctrl` device trees and ACPI `QCOM0217` platforms. PDC wake mapping and dual-edge errata handling integrate with suspend/resume wake support. The ACPI table's reserved GPIOs integrate with firmware ownership constraints.

## Risks and Edge Cases

- DT and ACPI data expose different capabilities. ACPI lacks function and wake map data and reserves GPIOs; consumers must not assume the DT function table is present on ACPI systems.
- The probe branch logs and fails if neither OF nor ACPI is present, which is correct but makes firmware matching mandatory.
- Absolute base offsets in group tables can silently misroute register accesses if a tile base is wrong.
- `.wakeirq_dual_edge_errata = true` is essential for correct dual-edge wake handling on affected GPIOs.
- `.ngpios` differs between DT and ACPI (`151` vs `150`), and the pin array also includes UFS/SDC descriptors. Off-by-one changes can expose unsupported pins.
- Special SDC/UFS groups disable many bit fields and must not be treated as normal GPIO-capable groups.

## Test Signals

Compile tests should cover both OF and `CONFIG_ACPI` builds. Runtime signals include successful probe for DT compatible `qcom,sdm845-pinctrl` and ACPI ID `QCOM0217`, correct GPIO counts/reservations for each firmware path, pinctrl debugfs function/group visibility on DT systems, ACPI GPIO availability matching reserved lists, pin state application for major peripherals, PM suspend/resume through `msm_pinctrl_dev_pm_ops`, GPIO IRQ tests including dual-edge behavior, and PDC wake tests using `sdm845_pdc_map[]`.
