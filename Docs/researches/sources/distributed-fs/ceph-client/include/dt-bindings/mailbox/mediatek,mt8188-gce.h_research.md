<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/mediatek,mt8188-gce.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/mediatek,mt8188-gce.h

## Purpose
This large binding header defines MediaTek MT8188 GCE/CMDQ constants: thread priorities, register subsystem IDs, hardware event IDs, sync tokens, handshake events, timeout tokens, and resource tokens used by command queue clients.

## Important APIs, types, and functions
The exported API is macro-only. Key groups are `CMDQ_THR_PRIO_*`, `SUBSYS_*`, event IDs for IMG/CAM/VPP/VDO/VDEC/VENC/WPE/DISP blocks (`CMDQ_EVENT_*`), synchronization tokens (`CMDQ_SYNC_TOKEN_*`), resource tokens such as `CMDQ_SYNC_RESOURCE_WROT0`, and output pin events.

## Control flow
MT8188 DTS and MediaTek multimedia drivers include the header to describe mailbox channels and command queue waits/signals. During preprocessing, symbolic events become numeric IDs that the GCE mailbox/CMDQ driver uses in command packets and event waits.

## State and persistence
The header has no state. Event and token numbers are hardware-facing ABI values embedded in DTBs and driver code; the actual state lives in GCE event registers, sync token state, and command queue threads.

## Dependencies and integration points
It integrates with the MediaTek CMDQ mailbox driver, display pipeline, image processing, camera, video decode/encode, VPP/VDO, WPE, MML, secure thread handling, and any client that waits for frame-done, start-of-frame, underrun, mutex, or handshake events.

## Risks and test signals
Risks include duplicate or wrong event IDs, sparse ranges hiding omissions, misuse of sync tokens as hardware events, and driver/DTS drift across MT8188 revisions. Test signals include DTS preprocessing, CMDQ mailbox probe, command queue wait/signal tests for display and camera, multimedia pipeline stress, timeout-token behavior, and event tracing during frame-done and underrun scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/mediatek,mt8188-gce.h -->
