# sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Makefile Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Makefile -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Makefile

### Purpose
The Makefile wires the DPAA2 QDMA driver into kbuild. When `CONFIG_FSL_DPAA2_QDMA` is enabled, it builds both the DMAengine driver and the DPDMAI Management Complex command wrapper.

### Important APIs, Types, And Functions
The only build rule is `obj-$(CONFIG_FSL_DPAA2_QDMA) += dpaa2-qdma.o dpdmai.o`.

### Control Flow, State, And Persistence
There is no runtime behavior. The object list ensures `dpaa2-qdma.c` can call the exported DPDMAI functions in `dpdmai.c` within the same built-in or module unit.

### Dependencies, Integration Points, Risks, And Test Signals
This file must stay aligned with the Kconfig symbol and source filenames. Risks include omitting `dpdmai.o`, which would break MC command symbols, or renaming files without updating kbuild. Test signals are module link success, built-in link success, and `modinfo` showing the DPAA2 QDMA module when built as `m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Makefile -->
