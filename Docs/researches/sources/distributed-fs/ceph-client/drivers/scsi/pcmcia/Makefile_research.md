# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/Makefile

Purpose: Kbuild mapping from PCMCIA SCSI config symbols to module objects.

Important entries: `ccflags-y` adds `drivers/scsi` to includes. `obj-$(CONFIG_PCMCIA_*)` emits `qlogic_cs.o`, `fdomain_cs.o`, `aha152x_cs.o`, `nsp_cs.o`, and `sym53c500_cs.o`. Composite objects are `aha152x_cs-objs := aha152x_stub.o aha152x_core.o` and `qlogic_cs-objs := qlogic_stub.o`.

Control flow/state: build-time only; no runtime state. It determines module composition and shared-core linkage.

Dependencies/integration: tied to the local Kconfig and shared SCSI core headers/sources.

Risks/test signals: object lists must match symbols and module aliases. Test by building each selected module, especially AHA152X composite linkage and shared include resolution.
