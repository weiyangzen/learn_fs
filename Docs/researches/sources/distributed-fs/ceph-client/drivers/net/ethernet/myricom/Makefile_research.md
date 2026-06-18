# sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/Makefile

Purpose: vendor-level Kbuild glue for Myricom Ethernet support.

Important declaration: `obj-$(CONFIG_MYRI10GE) += myri10ge/` descends into the Myri-10G driver directory when configured.

Control flow: build-time only.

State and persistence: no runtime state.

Dependencies and integration: paired with `myricom/Kconfig` and `myricom/myri10ge/Makefile`.

Risks: symbol mismatch would prevent driver compilation. The file currently has a single target, so behavior is straightforward.

Test signals: kernel builds with `CONFIG_MYRI10GE` set to built-in, module, and disabled.
