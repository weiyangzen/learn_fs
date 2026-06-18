# sources/distributed-fs/ceph-client/drivers/reset/sti/Makefile

Purpose: Kbuild mapping for STi reset support.

Important APIs/types/functions: `obj-$(CONFIG_STIH407_RESET) += reset-stih407.o reset-syscfg.o` builds the SoC data file and generic syscfg reset implementation together.

Control flow: no runtime behavior; build-time object selection only.

State and persistence: no runtime state.

Dependencies and integration: ensures `reset-stih407.c` has the `syscfg_reset_probe()` implementation available from `reset-syscfg.c`.

Risks and test signals: omitting either object causes unresolved symbols or no device data. Test with `CONFIG_STIH407_RESET=y` and disabled configs.
