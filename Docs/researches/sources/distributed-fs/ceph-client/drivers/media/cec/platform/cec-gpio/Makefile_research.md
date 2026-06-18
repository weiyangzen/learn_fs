# sources/distributed-fs/ceph-client/drivers/media/cec/platform/cec-gpio/Makefile

Purpose: This Makefile maps the generic GPIO CEC platform driver config to its object file.

Important APIs, types, and functions: `obj-$(CONFIG_CEC_GPIO) += cec-gpio.o`.

Control flow and state: Kbuild compiles `cec-gpio.c` when `CONFIG_CEC_GPIO` is enabled.

State and persistence behavior: Build-only.

Dependencies and integration points: Integrates the platform/CEC Kbuild tree with the GPIO bit-banged driver.

Risks and edge cases: Object name must remain aligned with source file and module expectations.

Test signals: Build `CEC_GPIO=y` and `CEC_GPIO=m`.
