# sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8173-gce.h

## Purpose
Defines MT8173 GCE/CMDQ thread priorities, subsystem codes, and display event IDs.

## Important APIs, Types, and Constants
Exports `CMDQ_THR_PRIO_LOWEST` and `CMDQ_THR_PRIO_HIGHEST`, `SUBSYS_1400XXXX` through `SUBSYS_1402XXXX`, and display events such as OVL/RDMA/WDMA/COLOR SOF, mutex stream EOF, and RDMA underrun events.

## Control Flow and State
No runtime logic. CMDQ packets and waits are interpreted by the MediaTek GCE driver and hardware.

## Dependencies and Integration Points
Self-contained DT binding used by MT8173 display subsystem nodes and CMDQ-aware drivers.

## Risks and Test Signals
Wrong subsystem or event IDs can make register access or synchronization target the wrong block. Test signals include DT schema validation and display pipeline testing under vblank, mutex EOF, and underrun conditions.
