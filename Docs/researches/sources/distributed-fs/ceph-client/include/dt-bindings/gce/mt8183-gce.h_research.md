# sources/distributed-fs/ceph-client/include/dt-bindings/gce/mt8183-gce.h

## Purpose
Defines MT8183 GCE/CMDQ timeout, priority, subsystem, and event constants for display, image, video, camera, and IPU synchronization.

## Important APIs, Types, and Constants
Exports `CMDQ_NO_TIMEOUT` as `0xffffffff`, priority constants, subsystem address-window IDs, and `CMDQ_EVENT_*` values for display mutex/vblank/stream EOF, MDP, ISP, camera, VENC/VDEC, and IPU done signals. Values are sparse and include high IPU event ranges.

## Control Flow and State
No control flow. The constants drive command queue packet behavior at runtime, but state is in GCE threads, event registers, and driver-managed packets.

## Dependencies and Integration Points
Self-contained header included by MediaTek MT8183 DTs and CMDQ client drivers for display/media pipelines.

## Risks and Test Signals
Timeout constants and event IDs directly affect synchronization. Misnumbering can cause timeouts, hangs, or data corruption in media pipelines. Test signals include DT checks and runtime tests for display, MDP, camera, video codec, and IPU workloads.
