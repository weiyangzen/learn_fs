# sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/Makefile

Purpose: maps SiS Ethernet Kconfig symbols to object files.

Important entries: `obj-$(CONFIG_SIS190) += sis190.o` and `obj-$(CONFIG_SIS900) += sis900.o`.

Integration and state: kbuild-only; no runtime state or driver logic appears here.

Risks and tests: object mapping must stay aligned with Kconfig symbol names and source files. Test module and built-in builds for both SiS drivers.
