# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8226.c

## Purpose
Describes the Qualcomm MSM8226 TLMM pin controller. It exposes 117 GPIOs plus SDC1/SDC2 storage groups, declares a focused function set for BLSP, camera clocks, CCI I2C, audio PCM, GP clocks, SDC3, and WLAN, and provides an MPM wake IRQ map for selected GPIOs.

## Important APIs, Types, And Data
`PINGROUP()` creates eight-slot GPIO mux groups using the older compact TLMM layout at `0x1000 + 0x10 * id`, two-bit interrupt detection, target bit 5, KPSS target value 4, and standard pull/drive/OE/value bits. `SDC_PINGROUP()` defines storage pad groups with only pull and drive valid. `msm8226_functions[]` is marked by a TODO that not all possible hardware functions are represented. `msm8226_mpm_map[]` maps wake-capable GPIOs to MPM interrupt numbers. `msm8226_pinctrl` sets `.ngpios = NUM_GPIO_PINGROUPS` and attaches the wake map.

## Control Flow
The `msm8226-pinctrl` platform driver is registered from `arch_initcall`. OF match `qcom,msm8226-pinctrl` calls `msm8226_pinctrl_probe()`, which delegates to `msm_pinctrl_probe()`. The common core registers the pinctrl device, adds the declared pinfunctions, exposes GPIOs 0-116, and uses the MPM wake map if a `wakeup-parent` is supplied by firmware.

## State And Persistence
The file contains no mutable state. It defines static pin/function/group topology and wake mapping. Hardware register state, IRQ masks, software dual-edge state, and mux-disable bookkeeping live in `pinctrl-msm.c`. The SDC groups are beyond `.ngpios`, preventing normal gpiolib access.

## Dependencies And Integration Points
Integrates with the shared MSM TLMM core, OF platform matching, gpiolib, pinctrl consumers, and MPM wake-parent irqdomain support. Device trees depend on group names `gpio0` through `gpio116`, `sdc1_*`, `sdc2_*`, and functions such as `blsp_uart*`, `blsp_spi*`, `blsp_i2c*`, `audio_pcm`, `cam_mclk*`, `cci_i2c0`, `sdc3`, and `wlan`.

## Risks
The explicit TODO means the mux table may be incomplete relative to hardware, so unsupported alternate functions may require future additions. Large ranges of groups are placeholders with `NA`, and incorrect assumptions by board files can cause failed pinctrl state selection. Wake map mistakes break suspend wake. SDC groups have invalid IRQ/mux fields and must not be counted as GPIOs. A wrong function order inside `PINGROUP()` changes the hardware mux selector written by the core.

## Test Signals
Test signals include probe success, 117 GPIO lines exposed, BLSP and camera/CCI pinctrl states applying correctly, WLAN/SDC3 mux validation, GPIO IRQ edge/level testing, MPM wake testing for mapped GPIOs, and storage-card pull/drive validation for SDC1/SDC2 groups.
