# sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/Makefile

Purpose: build rule for the SiFive PDMA DMAEngine driver.

Important APIs/types/functions: `obj-$(CONFIG_SF_PDMA) += sf-pdma.o` builds the single implementation file when the Kconfig symbol is enabled.

Control flow: kernel kbuild includes this object as built-in or module according to `CONFIG_SF_PDMA`.

State/persistence: no runtime state.

Dependencies/integration: depends on the parent DMA Makefile including this directory and the Kconfig symbol being visible.

Risks: there are no split objects, so any future helper files must be added here or they will not build.

Test signals: verify `CONFIG_SF_PDMA=y` links built-in and `CONFIG_SF_PDMA=m` emits the module object.
