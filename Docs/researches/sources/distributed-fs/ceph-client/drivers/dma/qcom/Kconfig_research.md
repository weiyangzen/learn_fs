# sources/distributed-fs/ceph-client/drivers/dma/qcom/Kconfig Research

## Purpose
This Kconfig fragment defines build-time options for Qualcomm DMA drivers under `drivers/dma/qcom`. In this subset it is most relevant because it declares `CONFIG_QCOM_BAM_DMA`, the symbol that builds `bam_dma.c`.

## Important APIs, Types, and Functions
There are no runtime APIs. The entries are `QCOM_ADM`, `QCOM_BAM_DMA`, `QCOM_GPI_DMA`, `QCOM_HIDMA_MGMT`, and `QCOM_HIDMA`. Each is a tristate except `QCOM_GPI_DMA` is also tristate and limited to `ARCH_QCOM`. All select `DMA_ENGINE`; ADM, BAM, and GPI also select `DMA_VIRTUAL_CHANNELS`.

`QCOM_BAM_DMA` is titled `QCOM BAM DMA support`, depends on `ARCH_QCOM || (COMPILE_TEST && OF && ARM)`, and enables the BAM DMA controller used by on-chip devices.

## Control Flow
Kconfig evaluation exposes these symbols to kernel configuration. If `QCOM_BAM_DMA` is enabled, the qcom DMA Makefile adds `bam_dma.o` to the build. Dependency expressions allow native Qualcomm builds and constrained compile-test builds with OF and ARM.

## State and Persistence
The selected values persist in the kernel `.config` and determine built-in or module output. The file has no runtime state.

## Dependencies and Integration Points
This file integrates with the parent DMA Kconfig menu and qcom DMA Makefile. The `select DMA_VIRTUAL_CHANNELS` dependency is required by BAM and ADM source code because they use the virt-dma helper layer.

## Risks and Edge Cases
Incorrect dependencies can either hide useful compile coverage or allow invalid builds. BAM compile-test is limited to `OF && ARM`, which reflects its device-tree and architecture assumptions. HIDMA management and channel options do not select virtual channels, matching their separate implementation model.

## Test Signals
Configuration tests should verify that enabling `QCOM_BAM_DMA=m` builds `bam_dma.ko`, that disabling it omits `bam_dma.o`, and that `COMPILE_TEST` configurations only expose it when OF and ARM constraints are satisfied.
