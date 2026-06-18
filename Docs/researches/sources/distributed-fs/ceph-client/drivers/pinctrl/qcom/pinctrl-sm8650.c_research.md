# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8650.c

## Purpose
This file is the Qualcomm SM8650 main TLMM pin controller descriptor. It provides static SoC metadata for 214 pins, 211 GPIO-visible lines, special UFS/SDC2 groups, mux functions, eGPIO support, interrupt bit layout, wake IRQ mapping, and the platform driver for `qcom,sm8650-tlmm`.

## Important APIs, Types, And Functions
`sm8650_tlmm` is the `struct msm_pinctrl_soc_data` passed to `msm_pinctrl_probe()`. It uses `sm8650_pins`, `sm8650_functions`, `sm8650_groups`, and `sm8650_pdc_map`, sets `ngpios = 211`, and uses `egpio_func = 10`. The `PINGROUP()` macro supports eleven mux entries per GPIO. It includes `i2c_pull_bit = 13`, eGPIO fields, interrupt wakeup presence/enable bits at 6 and 7, and an interrupt target bit at 8 rather than the older target bit 5 layout. `UFS_RESET(pg_name, ctl, io)` separates the control and I/O offsets, using `0xde004` and `0xdf000` for the SM8650 UFS reset group.

## Control Flow
The driver registers early with `arch_initcall()`. Matching `qcom,sm8650-tlmm` calls `sm8650_tlmm_probe()`, which delegates initialization to the shared Qualcomm MSM pinctrl core. At runtime, pinctrl selection indexes the SoC-specific function arrays and groups to compute mux values and register offsets. GPIO/IRQ operations similarly use per-group bit metadata and the 93-entry wake IRQ map for PDC integration.

## State And Persistence
All SoC-specific state here is static. Runtime state is held by the shared pinctrl core. TLMM register settings persist in hardware, including mux, pull, drive, output value, interrupt configuration, wake enable, and eGPIO state. The wake IRQ map is fixed metadata and is not modified at runtime.

## Dependencies And Integration Points
The file integrates with `pinctrl-msm`, platform/OF matching, gpiolib, IRQ/PDC wake handling, and device-tree pinctrl consumers. Its function set includes updated SM8650 routes such as GNSS ADC pins, `do_not` reserved mux slots, qlink little/big naming, camera AON MCLK2/MCLK4, i2chub, QUP1/QUP2 serial engines, QSPI/SDC4, audio I2S, UIM, USB, display vsync, CCI, QDSS, and eGPIO groups 165-209.

## Risks
SM8650 changes interrupt field layout and eGPIO mux slot compared with SM8450/SM8550; carrying older values forward would misroute interrupts or eGPIO muxing. The `do_not` mux entries should not be treated as normal consumer-facing functions without hardware validation. UFS reset uses non-contiguous control and I/O offsets, so generic assumptions of `io = ctl + 4` are not valid here. Wake IRQ map errors are suspend/resume failures rather than normal probe failures.

## Test Signals
Test signals include probe on `qcom,sm8650-tlmm`, 211 registered GPIOs, pinctrl state application for camera, CCI, QUP, i2chub, I2S, QSPI/SDC4, UIM, USB, qlink, and GNSS ADC routes, GPIO IRQ tests that validate the target bit 8 layout, wake-from-suspend coverage for mapped PDC lines, eGPIO mux tests using slot 10, and UFS reset/SDC2 pad validation.
