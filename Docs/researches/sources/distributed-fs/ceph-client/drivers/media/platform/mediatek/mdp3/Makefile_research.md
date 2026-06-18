# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/Makefile

## Purpose
This Makefile aggregates the MDP3 driver sources into the `mtk-mdp3` module/built-in object.

## Important APIs, Types, and Functions
It builds `mdp_cfg_data.o`, `mtk-mdp3-core.o`, `mtk-mdp3-vpu.o`, `mtk-mdp3-regs.o`, `mtk-mdp3-m2m.o`, `mtk-mdp3-comp.o`, and `mtk-mdp3-cmdq.o` under `obj-$(CONFIG_VIDEO_MEDIATEK_MDP3)`.

## Control Flow
Kbuild includes the aggregate object only when the Kconfig symbol is enabled.

## State and Persistence
No runtime state exists; the file defines build composition.

## Dependencies and Integration Points
The object list must stay synchronized with source files and Kconfig dependencies.

## Risks and Edge Cases
Missing one translation unit can break link-time symbols or silently remove runtime functionality such as CMDQ packet generation.

## Test Signals
Targeted driver builds and `allmodconfig` catch stale object references and unresolved symbols.
