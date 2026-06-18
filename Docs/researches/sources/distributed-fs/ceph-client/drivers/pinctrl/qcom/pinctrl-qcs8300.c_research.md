# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qcs8300.c

## Purpose
This file is the Qualcomm QCS8300 TLMM pin controller description consumed by the shared `pinctrl-msm` core. It enumerates QCS8300 pins, pin groups, mux functions, GPIO register layout, special SD/UFS groups, eGPIO-capable pads, QUP I3C mode offsets, and GPIO-to-PDC wake interrupt mappings. Runtime behavior is intentionally thin: the driver binds to `qcom,qcs8300-tlmm` and delegates almost all pinctrl, GPIO, and interrupt operations to `msm_pinctrl_probe()`.

## Important APIs, Types, And Functions
The file builds static tables for `struct pinctrl_pin_desc`, `struct pinfunction`, `struct msm_pingroup`, `struct msm_gpio_wakeirq_map`, and `struct msm_pinctrl_soc_data`. `PINGROUP()` is the central macro: for each GPIO it names the pinctrl group, supplies up to 11 alternate functions plus GPIO mode, and records register offsets and bit positions. QCS8300 differs from many older TLMM descriptions by carrying eGPIO register bits (`egpio_enable`, `egpio_present`) and declaring `.egpio_func = 11`, so the last mux slot is the eGPIO function for selected groups. `SDC_QDSD_PINGROUP()` models fixed SD card pads without GPIO/IRQ bits, while `UFS_RESET()` models the UFS reset output-only special group. `QUP_I3C()` and the QUP I3C offset constants describe I3C mode registers for selected QUP instances.

## Control Flow
Static initialization constructs the pin, function, group, and wake map tables. At `arch_initcall()` time `qcs8300_pinctrl_init()` registers a `platform_driver` named `qcs8300-tlmm`. OF matching on `qcom,qcs8300-tlmm` calls `qcs8300_pinctrl_probe()`, which passes `qcs8300_pinctrl` to the common MSM pinctrl core. From that point, mux selection, bias/drive configuration, GPIO direction/value operations, IRQ programming, wake IRQ mapping, and debugfs exposure are handled by `pinctrl-msm.c` using this file's data.

## State And Persistence
There is no mutable driver-private state in this file. All tables are `static const` and persist for the module lifetime. Hardware state lives in TLMM registers at 0x1000-byte GPIO strides and in special SD/UFS registers; the common core writes those registers in response to pinctrl, GPIO, and irqchip requests. Wake behavior depends on the static `qcs8300_pdc_map`. The eGPIO mode is data-driven by the group function slot and eGPIO present/enable bits.

## Dependencies And Integration Points
The driver depends on Linux platform driver and OF matching infrastructure plus `pinctrl-msm.h`. It integrates with device tree `pinctrl-*` states, the gpiolib provider registered by the MSM core, irqchip and PDC wake interrupt plumbing, serial/audio/display/camera/storage consumers named in the mux tables, SDHCI through `sdc1_*` groups, and UFS through `ufs_reset`. The `MODULE_DEVICE_TABLE(of, ...)` entry allows module autoloading for the compatible string.

## Risks And Test Signals
Risk is concentrated in data fidelity. A wrong mux slot changes a peripheral's selected function; a wrong register offset or bit index can affect unrelated pins; and a bad PDC mapping breaks suspend wake without breaking normal interrupts. The `ngpios = 134` boundary is important because the table also includes UFS/SD special groups beyond GPIO numbering. eGPIO pads from 110 through 132 need explicit validation because they rely on the extra mux function index and eGPIO status bits. Test signals include successful probe on a QCS8300 DT, pinctrl state application for QUP/I3C, audio, display, camera, SD, and UFS reset consumers, GPIO IRQ delivery and wake from mapped pads, and suspend/resume tests that verify PDC wake mappings.
