
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lgm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/lgm/Makefile

Purpose: maps the Lightning Mountain DMA Kconfig symbol to the driver object.

Important APIs and control flow: `obj-$(CONFIG_INTEL_LDMA) += lgm-dma.o` adds the LGM DMA implementation when the boolean Kconfig option is enabled.

State and persistence behavior: no runtime state exists; this file controls link-time inclusion.

Dependencies and integration points: depends on `CONFIG_INTEL_LDMA` from the same directory’s Kconfig and the parent kernel build system descending into `drivers/dma/lgm`.

Risks and test signals: risks are limited to symbol/name drift between Kconfig, Makefile, and source file. Test signals include `lgm-dma.o` appearing in built objects for enabled configs and absent for disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lgm/Makefile -->
