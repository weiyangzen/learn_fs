# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8909.c

## Purpose
Defines the Qualcomm MSM8909 TLMM variant. It exposes 113 GPIOs and SDC/QDSD storage groups, declares a wide set of BLSP, QDSS, camera, audio, UIM, WCSS, analog-test, power/modem/navigation, and miscellaneous functions, and maps wake-capable GPIOs to MPM interrupts.

## Important APIs, Types, And Data
`PINGROUP()` uses modern 0x1000-per-GPIO register spacing, ten mux slots, standard pull/drive/OE/value bits, KPSS target bit 5/value 4, and two-bit interrupt detection. `SDC_QDSD_PINGROUP()` provides storage pad groups with only pull/drive fields. `msm8909_functions[]` is built from `MSM_PIN_FUNCTION()` and `MSM_GPIO_PIN_FUNCTION(gpio)`. `msm8909_mpm_map[]` maps selected GPIOs to MPM wake IRQs. `msm8909_pinctrl` binds pins/functions/groups with `.ngpios = 113` so SDC/QDSD groups remain outside gpiolib.

## Control Flow
The platform driver registers at `arch_initcall`. OF match `qcom,msm8909-tlmm` calls `msm8909_pinctrl_probe()`, which delegates to `msm_pinctrl_probe()`. The shared core registers the pinctrl device and gpiochip, installs the TLMM IRQ handler, and uses the wake map when a wake-parent domain is present. Runtime behavior is completely table-driven by group mux arrays and register offsets in this file.

## State And Persistence
There is no local mutable state. Persistent hardware state is TLMM register configuration for mux, pull, drive, GPIO direction/value, and interrupts. The common core owns IRQ bookkeeping and wake-parent skip state. The wake map statically determines which GPIOs may be translated to MPM wake IRQs.

## Dependencies And Integration Points
Integrates with `pinctrl-msm.c`, OF platform matching, gpiolib, generic pinctrl clients, TLMM interrupt handling, and MPM wake-parent irqdomain support. Consumers reference groups `gpio0` through `gpio112`, `sdc1_*`, `sdc2_*`, and `qdsd_*`; functions include BLSP instances, WCSS BT/FM/WLAN, QDSS trace/CTI, CCI/camera, CDC/MI2S/DMIC, UIM, SSBI, and power/modem/navigation indicators.

## Risks
MSM8909 has many overlapping mux choices, so incorrect function ordering in a `PINGROUP()` entry can silently select the wrong hardware function. Wake map errors affect suspend wake. Some groups contain duplicate or unusual entries, such as repeated `gpio24` in `ebi2_lcd_groups`, which may be intentional hardware aliasing but deserves caution during edits. SDC/QDSD groups have invalid mux/IRQ fields and rely on `.ngpios` excluding them. Board files requesting unsupported placeholder `_` functions will fail.

## Test Signals
Test by probing `qcom,msm8909-tlmm`, checking 113 GPIO lines, applying BLSP/CCI/WCSS/audio/UIM/QDSS pinctrl states, verifying GPIO direction/value and IRQ edge/level operation, validating MPM wake from mapped GPIOs, and confirming SDC1/SDC2/QDSD pull-drive settings on real storage interfaces.
