# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/Kconfig

## Purpose
This Kconfig entry exposes the newer MediaTek MDP v3 V4L2 mem2mem driver.

## Important APIs, Types, and Functions
The symbol is `VIDEO_MEDIATEK_MDP3`, a tristate option depending on IOMMU/compile-test, video device support, DMA, remoteproc, MediaTek MMSYS, CMDQ, and SCP. It selects vb2 DMA-contig and V4L2 mem2mem support.

## Control Flow
When enabled, Kbuild compiles the `mtk-mdp3` aggregate object from the Makefile. Runtime behavior is split across core, VPU, regs, mem2mem, component, and CMDQ files.

## State and Persistence
The selected value persists in `.config` and controls built-in/module/disabled driver state.

## Dependencies and Integration Points
MDP3 requires the SCP firmware path, command queue mailbox engine, MMSYS routing, DMA/IOMMU, and V4L2/vb2 infrastructure.

## Risks and Edge Cases
The dependencies are stricter than the legacy driver because runtime CMDQ and SCP are central. Compile-test coverage must keep these dependencies satisfiable across architectures.

## Test Signals
Use MediaTek SoC defconfigs, `allmodconfig`, `COMPILE_TEST`, and dependency warning checks.
