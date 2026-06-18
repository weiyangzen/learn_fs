# sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8192-gce.h

## Purpose
Defines MT8192 GCE/CMDQ constants for command priorities, timeout behavior, subsystem routing, GPR registers, display/media/camera events, buffer underrun events, and maximum event count.

## Important APIs, Types, and Constants
Exports `CMDQ_NO_TIMEOUT`, `CMDQ_TIMEOUT_DEFAULT`, priority levels 0-7, `SUBSYS_*` IDs, `GCE_GPR_R00`-`R15`, and `CMDQ_EVENT_*` IDs ending with underrun events and `CMDQ_MAX_HW_EVENT` 512.

## Control Flow and State
No local flow. GCE runtime state is managed by hardware threads and the CMDQ driver, which consume these IDs in packet waits/signals.

## Dependencies and Integration Points
Self-contained binding included by MT8192 DT and MediaTek CMDQ clients, especially display, MDP, imaging, and video pipelines.

## Risks and Test Signals
Events are synchronization points; bad IDs create hangs or early completions. The max-event value should remain consistent with hardware and driver bitmaps. Test with DT schema checks and runtime pipelines that exercise vblank, frame done, underrun, and media completion events.
