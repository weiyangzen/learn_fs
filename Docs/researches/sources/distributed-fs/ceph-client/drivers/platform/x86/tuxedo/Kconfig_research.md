# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/Kconfig

Purpose: top-level Kconfig include point for TUXEDO x86 platform drivers. It currently delegates all selectable options to `drivers/platform/x86/tuxedo/nb04/Kconfig`.

Important APIs and control flow: this file has no runtime APIs. Its only active statement is `source "drivers/platform/x86/tuxedo/nb04/Kconfig"`, so menu visibility, dependencies, and module descriptions are defined in the nested Kconfig.

State and dependencies: there is no state or persistence. The integration point is the kernel Kconfig parser and the parent `drivers/platform/x86` menu.

Risks and test signals: a bad source path hides all TUXEDO NB04 options from configuration. Tests are configuration-oriented: run `make olddefconfig`, `make menuconfig`, or Kconfig lint and confirm `CONFIG_TUXEDO_NB04_WMI_AB` is reachable through the platform x86 drivers menu.
