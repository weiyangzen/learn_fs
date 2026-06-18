# sources/distributed-fs/ceph-client/drivers/dma/qcom/Makefile Research

## Purpose
This Makefile maps Qualcomm DMA Kconfig symbols to objects built by Kbuild.

## Important APIs, Types, and Functions
There are no runtime functions. `obj-$(CONFIG_QCOM_ADM)` builds `qcom_adm.o`; `obj-$(CONFIG_QCOM_BAM_DMA)` builds `bam_dma.o`; `obj-$(CONFIG_QCOM_GPI_DMA)` builds `gpi.o`; `obj-$(CONFIG_QCOM_HIDMA_MGMT)` builds the composite `hdma_mgmt.o` from `hidma_mgmt.o` and `hidma_mgmt_sys.o`; and `obj-$(CONFIG_QCOM_HIDMA)` builds composite `hdma.o` from `hidma_ll.o`, `hidma.o`, and `hidma_dbg.o`.

## Control Flow
During Kbuild traversal, the selected configuration symbols decide which object files are compiled and linked into the kernel image or modules. For this subset, `CONFIG_QCOM_BAM_DMA=y/m` directly controls whether `bam_dma.c` participates in the build.

## State and Persistence
The Makefile affects build artifacts only. It has no runtime state or persistent data.

## Dependencies and Integration Points
It depends on symbols declared in the sibling Kconfig file and integrates with the parent `drivers/dma` Kbuild hierarchy. Composite object declarations for HIDMA ensure multiple C files link into one module/object.

## Risks and Edge Cases
Symbol/object mismatches would silently omit drivers or try to build the wrong source. The double space in `obj-$(CONFIG_QCOM_HIDMA) +=  hdma.o` is harmless to Kbuild but worth noting as cosmetic. BAM has a simple one-symbol-to-one-object mapping.

## Test Signals
Build tests should toggle each qcom DMA symbol and inspect whether the expected `.o` or module is produced. For this work item, enabling `CONFIG_QCOM_BAM_DMA` should compile `drivers/dma/qcom/bam_dma.o`.
