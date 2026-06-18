# sources/distributed-fs/ceph-client/drivers/firmware/meson/Makefile

Purpose: Builds the Amlogic secure monitor driver object.

Important APIs/types/functions: `obj-$(CONFIG_MESON_SM) += meson_sm.o`.

Control flow: No runtime flow. Kbuild includes the object according to `CONFIG_MESON_SM`.

State and persistence behavior: No state.

Dependencies and integration points: Integrates with `meson/Kconfig` and the firmware build subtree.

Risks and test signals: Build-only risk. Test built-in and module builds of `CONFIG_MESON_SM`.
