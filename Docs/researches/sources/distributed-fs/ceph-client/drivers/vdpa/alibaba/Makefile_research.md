# sources/distributed-fs/ceph-client/drivers/vdpa/alibaba/Makefile

Purpose: kbuild entry for Alibaba ENI vDPA.

Important APIs/types/functions: `obj-$(CONFIG_ALIBABA_ENI_VDPA) += eni_vdpa.o`.

Control flow: builds `eni_vdpa.c` into a module or built-in object according to `CONFIG_ALIBABA_ENI_VDPA`.

State and persistence: build-only file.

Dependencies and integration: reached from top-level `drivers/vdpa/Makefile`; depends on Kconfig gating for PCI MSI, X86, and legacy virtio-pci helpers.

Risks: no multi-object composition, so all driver logic must remain in `eni_vdpa.c` unless this file is updated.

Test signals: confirm `eni_vdpa.o` builds and module name matches expectation when config is `m`.
