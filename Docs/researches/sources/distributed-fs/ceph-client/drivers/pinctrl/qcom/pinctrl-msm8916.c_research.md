# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8916.c

## Purpose
This file is the Qualcomm MSM8916 TLMM pin controller description. It does not implement a new pinctrl algorithm; it supplies the common `pinctrl-msm` core with the MSM8916 pin list, mux-function catalog, function-to-group mappings, per-group register offsets/bit fields, GPIO count, and OF/platform-driver binding for `qcom,msm8916-pinctrl`. The described hardware covers 122 GPIO pingroups plus SDC1, SDC2, and QDSD non-GPIO pin groups.

## Important APIs, Types, And Functions
The main exported contract is `static const struct msm_pinctrl_soc_data msm8916_pinctrl`, which points at `msm8916_pins`, `msm8916_functions`, and `msm8916_groups`, and declares `.ngpios = NUM_GPIO_PINGROUPS` with `NUM_GPIO_PINGROUPS` equal to 122. `msm8916_pinctrl_probe()` delegates directly to `msm_pinctrl_probe(pdev, &msm8916_pinctrl)`. `msm8916_pinctrl_of_match` binds the compatible string, and `msm8916_pinctrl_driver` registers through an `arch_initcall`.

The file relies on the shared `pinctrl-msm.h` data types: `struct msm_pingroup` supplies group name/pins, mux selector list, GPIO control registers, interrupt registers, and bit positions; `struct msm_pinctrl_soc_data` is consumed by the common Qualcomm pinctrl, GPIO, and IRQ code. Local `PINGROUP()` rows describe each GPIO group with 10 mux choices including GPIO mode, register offsets at `0x1000 * id` plus fixed offsets for IO and interrupt registers, mux bit 2, pull bit 0, drive bit 6, output-enable bit 9, and two-bit interrupt detection. `SDC_PINGROUP()` rows describe storage-card and QDSD pins with no GPIO/IRQ support and only pull/drive fields.

## Control Flow
At boot or module load, `msm8916_pinctrl_init()` registers the platform driver early. When device-tree matching creates a platform device, probe hands the immutable SoC table to the common core. From that point, all runtime behavior is in `pinctrl-msm.c`: pinctrl state selection indexes into `msm8916_functions` and the `funcs` arrays embedded in each `PINGROUP`; GPIO requests use the first 122 groups; IRQ setup uses each group's interrupt register offsets and detection/polarity bits; SDC and QDSD groups can be configured for bias/drive but have mux and interrupt fields disabled with `-1`.

## State And Persistence
This source file defines only static, read-only SoC description tables. It stores no runtime state, has no persistent storage, and performs no direct MMIO. Hardware state is created later by the common driver when clients apply pinctrl states or GPIO/IRQ operations. That hardware state persists in TLMM registers until another pinctrl operation, reset, or power transition rewrites it. The only lifetime action in this file is platform-driver registration and unregistration.

## Dependencies And Integration Points
The file depends on Linux module, OF, platform-device, and pinctrl infrastructure plus the local `pinctrl-msm` core. It integrates with device tree via `qcom,msm8916-pinctrl`, with board DTS pin states through function and group names such as BLSP I2C/SPI/UART, CCI/camera clocks, MI2S, codec, QDSS trace, SD write protect, WLAN/test, PMIC/power, SDC, and QDSD groups. It does not provide a wakeirq map, reserved GPIO list, tile list, or SoC-specific PM callbacks; the generic core defaults apply.

## Risks And Test Signals
Risk is concentrated in table correctness. A wrong function enum order, `MSM_PIN_FUNCTION()` table entry, or `PINGROUP()` mux position changes the numeric selector programmed into TLMM. Incorrect register offsets or bit positions can break GPIO direction, bias, drive strength, or IRQ routing across a whole bank. The `.ngpios` value must stay at 122 so the non-GPIO SDC/QDSD groups are not exposed as GPIOs. Test signals include successful probe from the compatible string, expected GPIO chip size of 122, DTS pinctrl states resolving every named function/group, BLSP and camera pins switching to non-GPIO modes, GPIO IRQ polarity/edge tests, and storage-card pull/drive configuration without GPIO exposure.
