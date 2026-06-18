# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/Makefile

Purpose: build routing for the TUXEDO platform-driver subtree. It unconditionally descends into the `nb04/` subdirectory via `obj-y += nb04/`.

Important APIs and control flow: no C symbols are defined here. Kbuild visits `nb04/Makefile`, where object inclusion is gated by `CONFIG_TUXEDO_NB04_WMI_AB`.

State and dependencies: no runtime state. It depends on Kbuild directory traversal and the parent platform/x86 Makefile including this directory.

Risks and test signals: if this Makefile is not reached, NB04 driver objects never build even when Kconfig is enabled. Build tests should confirm `drivers/platform/x86/tuxedo/nb04/tuxedo_nb04_wmi_ab.o` appears for `CONFIG_TUXEDO_NB04_WMI_AB=y/m`.
