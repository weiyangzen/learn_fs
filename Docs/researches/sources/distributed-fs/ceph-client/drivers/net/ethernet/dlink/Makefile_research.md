<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Makefile

Purpose: Kbuild object list for D-Link Ethernet drivers.

Important build rules: `obj-$(CONFIG_DL2K) += dl2k.o` includes the DL2000/TC902x/IP1000A driver when `CONFIG_DL2K` is built-in or module. `obj-$(CONFIG_SUNDANCE) += sundance.o` does the same for the Sundance Alta driver.

Control flow: Kbuild expands `obj-y` entries into built-in objects and `obj-m` entries into modules based on the tristate values produced by Kconfig. This file has no conditionals beyond the standard `obj-$()` pattern.

State and persistence: Build state is driven by `.config`; no runtime state exists in this Makefile.

Dependencies and integration: Directly paired with `sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Kconfig`. It assumes source files `dl2k.c` and `sundance.c` exist in the same directory and that Kconfig selects needed helper libraries.

Risks: Symbol/name drift between Kconfig and Makefile would silently drop a driver from builds. Object names must match actual source filenames. There is no aggregate object or subdirectory recursion here.

Test signals: Build with `CONFIG_DL2K=y/m`, `CONFIG_SUNDANCE=y/m`, both disabled, and mixed built-in/module configurations; verify generated objects/modules include only the selected drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Makefile -->
