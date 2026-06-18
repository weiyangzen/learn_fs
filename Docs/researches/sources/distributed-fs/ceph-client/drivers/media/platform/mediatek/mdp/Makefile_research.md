# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/Makefile

## Purpose
This Makefile builds the legacy MediaTek MDP driver object from its core, component, mem2mem, register/VPU-configuration, and VPU transport sources.

## Important APIs, Types, and Functions
`mtk-mdp-y` aggregates `mtk_mdp_core.o`, `mtk_mdp_comp.o`, `mtk_mdp_m2m.o`, `mtk_mdp_regs.o`, and `mtk_mdp_vpu.o`. `obj-$(CONFIG_VIDEO_MEDIATEK_MDP)` emits the final `mtk-mdp` module or built-in object. `ccflags-y` adds the MediaTek VPU include directory.

## Control Flow
Kbuild evaluates `CONFIG_VIDEO_MEDIATEK_MDP` and compiles the aggregate object list if enabled.

## State and Persistence
There is no runtime state. The Makefile persists build composition.

## Dependencies and Integration Points
It is coupled to `Kconfig`, local source filenames, and `drivers/media/platform/mediatek/vpu` headers.

## Risks and Edge Cases
Renaming any source file or moving VPU headers requires synchronized Makefile changes. Missing one object can produce link failures or a driver without a core subsystem.

## Test Signals
Targeted `make drivers/media/platform/mediatek/mdp/`, `allmodconfig`, and module load checks are useful signals.
