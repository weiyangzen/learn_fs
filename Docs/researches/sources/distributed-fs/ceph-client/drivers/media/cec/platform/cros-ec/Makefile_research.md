# sources/distributed-fs/ceph-client/drivers/media/cec/platform/cros-ec/Makefile

Purpose: This Makefile maps the ChromeOS EC CEC platform driver config to its object file.

Important APIs, types, and functions: `obj-$(CONFIG_CEC_CROS_EC) += cros-ec-cec.o`.

Control flow and state: Kbuild builds the ChromeOS EC CEC driver when the config symbol is enabled.

State and persistence behavior: Build-only.

Dependencies and integration points: Integrates the platform CEC Kbuild tree with the ChromeOS EC CEC implementation.

Risks and edge cases: Must stay aligned with Kconfig and source file name for module builds.

Test signals: Build `CEC_CROS_EC=y` and `CEC_CROS_EC=m` with CROS_EC protocol support.
