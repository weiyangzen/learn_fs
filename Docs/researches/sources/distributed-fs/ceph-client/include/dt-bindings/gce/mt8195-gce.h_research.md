# sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8195-gce.h

## Purpose
Defines the large MT8195 GCE/CMDQ binding surface: timeout constants, thread priorities, CPR register count, subsystem windows, GPR registers, and hundreds of hardware event IDs for imaging, display, video, HDMI, DP, WPE, and software output pins.

## Important APIs, Types, and Constants
Exports `CMDQ_NO_TIMEOUT`, `CMDQ_TIMEOUT_DEFAULT`, `CMDQ_THR_PRIO_*`, `GCE_CPR_COUNT` 1312, `SUBSYS_*`, `GCE_GPR_R00` through `R15`, and `CMDQ_EVENT_*` IDs. The event namespace reaches `CMDQ_EVENT_OUTPIN_1` 1019 and defines `CMDQ_MAX_HW_EVENT` 1019.

## Control Flow and State
No executable flow in the header. Runtime state is in GCE event registers, command queue threads, GPR/CPR registers, and CMDQ driver packet state.

## Dependencies and Integration Points
Self-contained binding used by MT8195 DT nodes and high-level MediaTek display, camera, video, and image-processing drivers that synchronize work through CMDQ.

## Risks and Test Signals
The breadth of event IDs creates high collision and stale-ID risk. Max-event handling must match driver allocation sizes. Test signals include DT validation, CMDQ packet tests, and end-to-end display, camera, video codec, HDMI/DP, and WPE pipeline tests under completion and timeout scenarios.
