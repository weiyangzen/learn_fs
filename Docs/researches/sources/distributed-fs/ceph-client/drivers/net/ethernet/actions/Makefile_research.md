# sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/Makefile

Purpose: this Kbuild file compiles the Actions Semi Owl EMAC driver when its Kconfig symbol is enabled.

Important APIs, types, and functions: the only build rule is `obj-$(CONFIG_OWL_EMAC) += owl-emac.o`.

Control flow: Kbuild descends into this directory when `CONFIG_NET_VENDOR_ACTIONS` enables the vendor directory in the parent Makefile. If `CONFIG_OWL_EMAC=y`, `owl-emac.o` is built into the kernel; if `m`, it becomes a module; if disabled, no object is produced.

State and persistence: no runtime state. Build outputs depend on `.config` and Kbuild.

Dependencies and integration points: depends on `actions/Kconfig` defining `CONFIG_OWL_EMAC` and on `owl-emac.c`/`owl-emac.h` being present. It integrates with module metadata in `owl-emac.c`.

Risks: because the Makefile is minimal, any future split of `owl-emac` into multiple objects would require updating this line into a composite-object rule. A symbol rename in Kconfig without this Makefile change would silently stop building the driver.

Test signals: targeted build with `CONFIG_NET_VENDOR_ACTIONS=y` and `CONFIG_OWL_EMAC=m/y`; verify `owl-emac.o` or module output exists and no stale object names are referenced.
