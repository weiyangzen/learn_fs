# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ar5523/Makefile

Purpose: Kbuild mapping for the AR5523 driver.

Important APIs/types/functions: `obj-$(CONFIG_AR5523) := ar5523.o` compiles and links the single-source driver when the Kconfig symbol is enabled.

Control flow: Kbuild includes this directory from the Atheros parent Makefile. A disabled `CONFIG_AR5523` produces no objects; built-in or module selection produces the corresponding kernel object/module.

State/persistence: Build artifact only; no runtime state.

Dependencies/integration: Depends on the parent `ath/Makefile` and the `AR5523` Kconfig entry. The single object contains USB probe/disconnect, firmware loading, command protocol, and mac80211 operations.

Risks: Because all behavior is in one C file, any future split must update this Makefile or Kbuild will omit new objects.

Test signals: `make M=drivers/net/wireless/ath/ar5523 CONFIG_AR5523=m` should produce `ar5523.ko` with no unresolved symbols when mac80211, USB, firmware loader, and Atheros common support are available.
