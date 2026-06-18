# sources/distributed-fs/ceph-client/drivers/media/cec/platform/meson/Makefile

Purpose: This Makefile maps Amlogic Meson CEC config symbols to their platform driver objects.

Important APIs, types, and functions: `obj-$(CONFIG_CEC_MESON_AO) += ao-cec.o` and `obj-$(CONFIG_CEC_MESON_G12A_AO) += ao-cec-g12a.o`.

Control flow and state: The parent platform Makefile always descends into `meson/`; this file gates each Meson object by its config symbol.

State and persistence behavior: Build-only.

Dependencies and integration points: Integrates Meson AO CEC driver variants with Kbuild. The G12A variant depends on regmap MMIO/common clock/OF per Kconfig.

Risks and edge cases: Object names must match source files and Kconfig symbols. The unconditional parent descent means this file must not add unguarded objects.

Test signals: Build `CEC_MESON_AO` and `CEC_MESON_G12A_AO` as modules and built-ins, including COMPILE_TEST configurations.
