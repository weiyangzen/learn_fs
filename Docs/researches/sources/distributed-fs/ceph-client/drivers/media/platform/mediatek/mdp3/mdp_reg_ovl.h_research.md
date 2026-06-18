# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_ovl.h

## Purpose
This header defines MDP3 OVL block offsets and masks for overlay relay/layer sizing used in advanced MT8195 paths.

## Important APIs, Types, and Functions
Macros cover enable, ROI size, datapath control, source control, layer 0 control, and layer 0 source size.

## Control Flow
OVL component ops enable relay mode during init, configure layer/source frame bits, and write ROI/source size per subframe.

## State and Persistence
The OVL state is volatile command-queue-programmed MMIO state.

## Dependencies and Integration Points
Included by `mtk-mdp3-comp.c` for OVL components selected by static SoC data.

## Risks and Edge Cases
Overlay relay setup must match downstream ROI sizes or paths can hang/produce clipped output. Reserved-bit masks must stay correct.

## Test Signals
OVL path CMDQ traces and output-size validation across tiled subframes.
