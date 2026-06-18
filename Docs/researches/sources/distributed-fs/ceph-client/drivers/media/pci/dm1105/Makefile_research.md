# sources/distributed-fs/ceph-client/drivers/media/pci/dm1105/Makefile

Purpose: builds the DM1105 driver object when `CONFIG_DVB_DM1105` is enabled.

Important APIs/types/functions: `obj-$(CONFIG_DVB_DM1105) += dm1105.o` and `ccflags-y += -I $(srctree)/drivers/media/dvb-frontends`.

Control flow: participates in Kbuild only; no runtime behavior.

State and persistence: no state.

Dependencies/integration: adds include path for DVB frontend headers used directly by `dm1105.c`.

Risks and test signals: stale include flags or object names break compilation. Test via modular and built-in builds with `CONFIG_DVB_DM1105=m/y`.
