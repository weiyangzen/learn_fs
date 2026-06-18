# sources/distributed-fs/ceph-client/drivers/net/ethernet/ni/Makefile

Purpose: Connects the NI XGE management Ethernet Kconfig symbol to its object file.

Important APIs/types/functions: `obj-$(CONFIG_NI_XGE_MANAGEMENT_ENET) += nixge.o`.

Control flow/state: Build-system rule only. Runtime behavior comes from `nixge.c` when the symbol is enabled.

Dependencies/integration: Consumed by Kbuild under `drivers/net/ethernet/ni`; paired with `Kconfig`.

Risks: Symbol/file name drift would silently omit or fail the driver build. There are no multi-object rules here.

Test signals: Build with `CONFIG_NI_XGE_MANAGEMENT_ENET=m` and `=y`, verify `nixge.o` is compiled/linked in the expected target.
