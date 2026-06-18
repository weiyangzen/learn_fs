# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/Makefile

Purpose: this child Makefile defines the Broadcom ASP2 module composition. It turns `CONFIG_BCMASP` into a `bcm-asp.o` composite object.

Important APIs/types/functions: `obj-$(CONFIG_BCMASP) += bcm-asp.o` declares the module/built-in target, and `bcm-asp-objs := bcmasp.o bcmasp_intf.o bcmasp_ethtool.o` lists the three implementation objects linked into that target.

Control flow: kbuild includes this file only when the parent Broadcom Makefile descends into `asp2/`. It then compiles and links the core platform driver, per-interface netdev implementation, and ethtool support into one module.

State and persistence: there is no runtime state. Build state is derived from `CONFIG_BCMASP` and the object list.

Dependencies and integration points: this file must match exported/internal symbols across `bcmasp.c`, `bcmasp_intf.c`, `bcmasp_ethtool.c`, and declarations in `bcmasp.h`. `bcmasp_ethtool_ops` is defined in the ethtool object and referenced by interface creation; IRQ/filter/clock helpers are defined in the core object and used by the interface object.

Risks: omitted objects produce unresolved symbols or missing netdev capabilities. Renaming `bcm-asp.o` or its components must be coordinated with module aliases and Kconfig help. Test signals are a clean module build and `modinfo`/link checks showing `bcmasp.o`, `bcmasp_intf.o`, and `bcmasp_ethtool.o` included.
