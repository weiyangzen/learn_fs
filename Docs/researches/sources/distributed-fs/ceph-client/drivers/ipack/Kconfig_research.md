# sources/distributed-fs/ceph-client/drivers/ipack/Kconfig

Purpose: Defines the top-level `IPACK_BUS` menu option and includes carrier/device submenus when the IndustryPack framework is enabled.

Important APIs/types/functions: `menuconfig IPACK_BUS`, dependency `HAS_IOMEM`, and `source` statements for `drivers/ipack/carriers/Kconfig` and `drivers/ipack/devices/Kconfig`.

Control flow: Kconfig exposes a tristate bus framework. If selected, the nested carrier and device driver options become visible. If disabled, neither TPCI200 carrier nor IP-OCTAL device config entries are reachable through this subtree.

State and persistence: No runtime state. Build configuration persists through `.config`, influencing whether `ipack.o` and child directories are compiled.

Dependencies/integration: It is the configuration gate for the IPACK bus core and any module drivers consuming `<linux/ipack.h>`.

Risks and test signals: Confirm `HAS_IOMEM=n` hides the option; `IPACK_BUS=m` permits modular carrier/device builds; and disabling `IPACK_BUS` removes child driver symbols from configuration resolution.
