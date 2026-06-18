# sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8186-gce.h

## Purpose
Defines MT8186 GCE/CMDQ command constants for priorities, CPR count, subsystem routing, GPR registers, hardware events, software tokens, timer tokens, and event maximums.

## Important APIs, Types, and Constants
Exports `CMDQ_NO_TIMEOUT`, `CMDQ_TIMEOUT_DEFAULT`, eight priority levels, `GCE_CPR_COUNT`, `SUBSYS_*` address-window IDs, `GCE_GPR_R00` through `R15`, numerous `CMDQ_EVENT_*` IDs, `CMDQ_TOKEN_*` software synchronization tokens, and `CMDQ_EVENT_MAX` `0x3FF`.

## Control Flow and State
No executable code. Runtime state is the GCE command queue thread state, event flags, GPR registers, and software token state managed by the CMDQ driver.

## Dependencies and Integration Points
Self-contained binding used by MT8186 DT nodes and MediaTek display/media/camera drivers that use CMDQ synchronization.

## Risks and Test Signals
Event and token namespaces must not collide. `CMDQ_EVENT_MAX` constrains valid hardware event IDs. Test signals include DT validation plus runtime CMDQ workloads across display, MDP, camera, video, and token/timer waits.
