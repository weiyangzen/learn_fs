# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/Makefile

Purpose: Connects the Silicon Labs wireless vendor directory to Kbuild.

Important APIs and types: `obj-$(CONFIG_WFX) += wfx/` descends into the WFx subdirectory when `CONFIG_WFX` is enabled.

Control flow and integration: Build recursion is controlled entirely by `CONFIG_WFX`; actual object composition is in `silabs/wfx/Makefile`.

State and persistence: No runtime state. The built module/object set is persisted only in build artifacts.

Dependencies: Depends on `CONFIG_WFX` from `wfx/Kconfig`.

Risks and test signals: Build tests should verify `CONFIG_WFX=n` omits the directory and `CONFIG_WFX=m/y` descends correctly without duplicate objects.

Test signals: Source read size: 3 lines, 67 bytes.
