# sources/distributed-fs/ceph-client/include/dt-bindings/gce/mediatek,mt6795-gce.h

## Purpose
Defines MediaTek MT6795 GCE/CMDQ priorities and hardware event IDs for command queue synchronization.

## Important APIs, Types, and Constants
Exports thread priority constants from `CMDQ_THR_PRIO_LOWEST` through `CMDQ_THR_PRIO_HIGHEST` and a large `CMDQ_EVENT_*` set for mutex stream EOF, display blocks, MDP, ISP, camera, sensor FIFO, JPEG encode/decode, and related events. Event values are sparse and extend to JPEG events around 257-259.

## Control Flow and State
No executable flow. Runtime command execution, waits, and event signaling are handled by GCE hardware and the CMDQ driver.

## Dependencies and Integration Points
Self-contained header used by MT6795 DT nodes and MediaTek display/media drivers that submit CMDQ packets with event waits.

## Risks and Test Signals
Event IDs are synchronization ABI. Wrong values can deadlock command queues or signal completion early. Test signals include DT schema validation and runtime display/camera/JPEG pipelines using CMDQ waits and triggers.
