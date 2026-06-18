# sources/distributed-fs/ceph-client/drivers/platform/arm64/Kconfig

Purpose: Kconfig menu for ARM64 platform-specific, mostly EC-like, laptop/tablet drivers.

Important APIs, types, and functions: `ARM64_PLATFORM_DEVICES` is the parent menuconfig gated by `ARM64 || COMPILE_TEST`. Child tristates are `EC_ACER_ASPIRE1`, `EC_HUAWEI_GAOKUN`, `EC_LENOVO_YOGA_C630`, and `EC_LENOVO_THINKPAD_T14S`.

Control flow: enabling the parent reveals child drivers. Each child declares subsystem dependencies matching its source file: Acer needs I2C, DRM, POWER_SUPPLY, and INPUT; Huawei needs I2C, INPUT, HWMON, and selects AUXILIARY_BUS; Yoga C630 needs I2C and selects AUXILIARY_BUS; T14s needs I2C and INPUT plus LED and sparse-keymap support.

State and persistence: no runtime state. Selected tristate values drive module/built-in build results through the arm64 Makefile.

Dependencies and integration points: tied to Qualcomm/ARM64 laptop DT-described EC devices. Auxiliary-bus selects support downstream PSY/UCSI subdrivers for Huawei and Yoga C630.

Risks and edge cases: `COMPILE_TEST` broadens build coverage beyond real hardware. Missing dependencies can cause link failures; excessive dependencies can prevent useful compile coverage. The user-visible help emphasizes nonstandard battery/EC exposure compared with ACPI.

Test signals: all child symbols should compile as `m` under `COMPILE_TEST` with dependencies enabled. Runtime smoke tests are hardware-specific and should verify probe, IRQs, and subsystem registration.
