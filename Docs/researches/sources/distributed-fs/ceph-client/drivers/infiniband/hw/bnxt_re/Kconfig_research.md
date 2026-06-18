# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/Kconfig

Purpose: defines the kernel configuration symbol for the Broadcom NetXtreme-E RoCE driver.

Important APIs and build contract: `config INFINIBAND_BNXT_RE` is a tristate option with prompt `Broadcom Netxtreme HCA support`. It depends on `64BIT`, `INET`, `DCB`, and the Broadcom Ethernet driver symbol `BNXT`. The help text documents that the module name is `bnxt_re` and that it supports Broadcom NetXtreme-E 10/25/40/50 Gb RoCE HCAs.

Control flow: Kconfig selection controls whether the Makefile builds `bnxt_re.o` built-in, as a module, or not at all. No runtime code is present.

State and persistence: the selected symbol persists in kernel build configuration files such as `.config`; it does not create driver runtime state itself.

Dependencies and integration points: ties the RDMA driver to networking prerequisites and the underlying Broadcom Ethernet device support. The `DCB` and `INET` dependencies reflect RoCE’s Ethernet/IP and data-center-bridging integration points.

Risks: missing or too-weak dependencies can produce build failures or runtime feature gaps. Overly strict dependencies can hide the driver on valid platforms. The option is limited to 64-bit builds.

Test signals: Kconfig resolution tests across built-in/module combinations, allmodconfig/allnoconfig builds, dependency-disabled builds that verify the option disappears, and module-load tests confirming the built artifact is named `bnxt_re`.
