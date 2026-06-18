# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8750.c

## Purpose
This file is the Qualcomm SM8750 main TLMM pin controller descriptor. It extends the later SM8x50 TLMM pattern to 219 pin descriptors, 216 GPIO-visible lines, extra eGPIO-only pads, SM8750-specific mux functions, PDC wake mappings, UFS reset, and SDC2 special groups. It binds to `qcom,sm8750-tlmm`.

## Important APIs, Types, And Functions
`sm8750_tlmm` supplies the shared MSM pinctrl driver with `sm8750_pins`, `sm8750_functions`, `sm8750_groups`, `sm8750_pdc_map`, `ngpios = 216`, and `egpio_func = 11`. `PINGROUP()` exposes twelve mux choices per GPIO and explicitly marks the final mux argument as the eGPIO mode slot. Like SM8650, it has interrupt wakeup present/enable bits at 6/7 and target bit 8. `UFS_RESET(pg_name, ctl, io)` uses SM8750 offsets `0xe2004` and `0xe3000`. `SDC_QDSD_PINGROUP()` defines SDC2 clock, command, and data pad control at `0xdb000`.

## Control Flow
`sm8750_tlmm_init()` registers the platform driver at `arch_initcall()` time. OF matching on `qcom,sm8750-tlmm` invokes `sm8750_tlmm_probe()`, which calls `msm_pinctrl_probe(pdev, &sm8750_tlmm)`. Runtime pinctrl, pinmux, pinconf, GPIO, and IRQ paths are all handled by the shared MSM implementation using the static tables from this file. The group table includes GPIO0-GPIO214 plus UFS and SDC2 groups, while `ngpios = 216` exposes GPIO0-GPIO215 to gpiolib.

## State And Persistence
The descriptor is static and immutable. Mutable state is in the common Qualcomm pinctrl core and in TLMM hardware registers. Register programming persists until reset, low-power restore, or a later pinctrl/gpio/irq operation. The PDC map statically maps 93 GPIO lines to wake IRQs.

## Dependencies And Integration Points
The file depends on `pinctrl-msm.h`, Linux platform/OF APIs, and the Qualcomm TLMM binding. It integrates with SM8750 board device trees and peripheral drivers for camera MCLK/CCI, i2chub/QUP serial engines, I2S audio, UIM, QSPI/SDC4, display MDP vsync/eSync, PCIe clock request, USB, qlink, WCN switch signals, GNSS ADC, test/debug functions, UFS reset, and SDC2 pads. It also has many eGPIO-capable groups from GPIO105 onward and GPIO165-GPIO215.

## Risks
This file increases the mux slot count and eGPIO index to 11; older assumptions from SM8650 would select the wrong function. `ngpios = 216` must remain consistent with the group table and special-group boundary so UFS/SDC pads are not exposed as normal GPIOs. SM8750 removes or renames some older routes and adds WCN, MDP eSync, MDP vsync5, and TSENSE PWM4 functions, making cross-SoC copy/paste risky. Wake IRQ numbers and UFS/SDC offsets are hardware-specific and are likely to fail only on targeted suspend or storage tests if wrong.

## Test Signals
Expected signals include successful platform probe, 216 GPIOs registered, working pinctrl states for camera, CCI, i2chub/QUP, I2S, UIM, QSPI/SDC4, USB, display vsync/eSync, qlink, WCN, and GNSS ADC functions, GPIO IRQ tests using the newer interrupt layout, wake-from-suspend tests for the PDC map, eGPIO tests on the final mux slot, UFS reset toggling at the SM8750 offsets, and SDC2 pad configuration at `0xdb000`.
