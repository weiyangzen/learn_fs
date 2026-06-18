# sources/distributed-fs/ceph-client/drivers/media/cec/platform/Kconfig

Purpose: This file defines platform CEC driver options for ChromeOS EC, Amlogic Meson, GPIO bit-banged CEC, Samsung S5P, STi/STM32, Tegra, and SECO board controllers, plus SECO RC5 support.

Important APIs, types, and functions: Config symbols include `CEC_CROS_EC`, `CEC_MESON_AO`, `CEC_MESON_G12A_AO`, `CEC_GPIO`, `CEC_SAMSUNG_S5P`, `CEC_STI`, `CEC_STM32`, `CEC_TEGRA`, `CEC_SECO`, and `CEC_SECO_RC`. Each selects `CEC_CORE`; many select `CEC_NOTIFIER`; GPIO selects `CEC_PIN` and `GPIOLIB`; Meson G12A and STM32 select regmap helpers.

Control flow and state: Driver visibility depends on architecture, `COMPILE_TEST`, firmware subsystems, GPIO/preemption, PCI/DMI, and RC core combinations. Selected drivers are compiled through the platform Makefile and subdirectories.

State and persistence behavior: Build-time `.config` only.

Dependencies and integration points: Ties CEC platform drivers to SoC/board subsystems, notifier physical-address integration, GPIO library, ChromeOS EC protocol, regmap MMIO, PCI/DMI, and RC core.

Risks and edge cases: Architecture and `COMPILE_TEST` gates must keep drivers buildable without making invalid runtime assumptions. GPIO CEC depends on preemption or compile test because software timing is latency-sensitive. SECO RC dependency must match built-in/module RC core compatibility.

Test signals: Kconfig/build tests across supported architectures and COMPILE_TEST, with notifier, regmap, GPIO, CROS_EC, PCI/DMI, and RC combinations.
