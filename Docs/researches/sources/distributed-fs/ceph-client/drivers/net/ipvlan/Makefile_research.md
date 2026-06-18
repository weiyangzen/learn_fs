# sources/distributed-fs/ceph-client/drivers/net/ipvlan/Makefile

Purpose: Defines the build objects for the ipvlan and ipvtap network drivers.

Important APIs and data: `obj-$(CONFIG_IPVLAN) += ipvlan.o` builds the ipvlan composite object when ipvlan is enabled. `obj-$(CONFIG_IPVTAP) += ipvtap.o` builds ipvtap separately. `ipvlan-objs-$(CONFIG_IPVLAN_L3S) += ipvlan_l3s.o` conditionally adds L3S support, and `ipvlan-objs := ipvlan_core.o ipvlan_main.o $(ipvlan-objs-y)` defines the base ipvlan object composition.

Control flow and integration: Kbuild evaluates the config symbols and links `ipvlan_core.o`, `ipvlan_main.o`, and optionally `ipvlan_l3s.o` into `ipvlan.o`. The built objects register rtnetlink/link operations and packet handlers elsewhere in the ipvlan subsystem.

State and persistence: No runtime state. Build outputs persist as kernel objects/modules according to Kconfig and build mode.

Dependencies: Depends on Kconfig symbols `CONFIG_IPVLAN`, `CONFIG_IPVTAP`, and `CONFIG_IPVLAN_L3S`, plus source files named in the object lists.

Risks: Missing conditional object linkage would compile out L3S hooks while headers still expose stubs or declarations. Object ordering is simple but should keep core/main linked into the composite ipvlan object.

Test signals: Build with ipvlan disabled, ipvlan enabled, ipvtap enabled, and `CONFIG_IPVLAN_L3S` toggled; verify module/object symbols and L3S registration availability.
