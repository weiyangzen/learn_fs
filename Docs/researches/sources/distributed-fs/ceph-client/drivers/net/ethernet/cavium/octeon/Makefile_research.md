# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/octeon/Makefile

Purpose: Build glue for Cavium Octeon management Ethernet support.

Important APIs, types, and functions: The file contains a single Kbuild rule: `obj-$(CONFIG_OCTEON_MGMT_ETHERNET) += octeon_mgmt.o`.

Control flow: During kernel build, enabling `CONFIG_OCTEON_MGMT_ETHERNET` compiles and links `octeon_mgmt.c` into the relevant built-in or module object according to the parent networking driver build.

State and persistence: No runtime state. It controls compilation only.

Dependencies and integration: Depends on the Kconfig symbol being selected in the Cavium network driver configuration. It integrates with parent `drivers/net/ethernet/cavium/Makefile`.

Risks: If the symbol is unset, the platform driver and management Ethernet support are absent. If object naming changes, this Makefile must track it.

Test signals: Kernel build with `CONFIG_OCTEON_MGMT_ETHERNET=y/m`, object presence in build logs, and no stale references after renaming source files.
