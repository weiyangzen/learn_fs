# sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/Makefile

Purpose: Kbuild file for the Myricom Myri-10G Ethernet driver.

Important declaration: `obj-$(CONFIG_MYRI10GE) += myri10ge.o` builds the single-source driver object/module.

Control flow: build-time only; all behavior is in `myri10ge.c`.

State and persistence: no runtime state.

Dependencies and integration: invoked from the Myricom vendor Makefile.

Risks: if the driver is split into more source files later, this file must be updated to a composite object declaration.

Test signals: `make M=drivers/net/ethernet/myricom/myri10ge` and full kernel builds in module and built-in modes.
