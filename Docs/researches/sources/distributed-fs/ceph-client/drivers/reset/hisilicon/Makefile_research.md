# sources/distributed-fs/ceph-client/drivers/reset/hisilicon/Makefile

Purpose: Kbuild mapping for HiSilicon reset drivers.

Important APIs/types/functions: `obj-$(CONFIG_COMMON_RESET_HI6220) += hi6220_reset.o` and `obj-$(CONFIG_COMMON_RESET_HI3660) += reset-hi3660.o`.

Control flow: build-time only.

State and persistence: no runtime state; object selection follows `.config`.

Dependencies and integration: ties the HiSilicon Kconfig symbols to the source files in this directory.

Risks and test signals: mismatched names break module/built-in builds. Test both symbols as modules and built-in where supported.
