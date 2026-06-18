# sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/Makefile

Purpose: Kbuild file for the B2C2 FlexCop PCI driver object.

Important APIs/types/functions: when `CONFIG_DVB_B2C2_FLEXCOP_PCI` is set, `b2c2-flexcop-pci-objs` includes `flexcop-dma.o`; it always includes `flexcop-pci.o` before `obj-$(CONFIG_DVB_B2C2_FLEXCOP_PCI) += b2c2-flexcop-pci.o`. `ccflags-y` adds the common FlexCop include path.

Control flow: Kbuild composes one module/built-in object from PCI glue plus DMA support under the driver config. The common include path lets PCI code include shared FlexCop headers.

State/persistence: build-only state.

Dependencies/integration: depends on common B2C2 FlexCop headers and the config symbol from the local Kconfig. Runtime integration is with the common FlexCop core and PCI bus driver files outside this work item.

Risks/test signals: the conditional addition of DMA object should match all configurations where PCI object is linked. Build tests should cover module and built-in builds, header include path validity, and no-object build when the config is disabled.
