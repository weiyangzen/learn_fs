<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/mt.h -->
# sources/distributed-fs/ceph-client/include/linux/input/mt.h

Purpose: Defines the input multitouch slot tracking library.

Important APIs/types/functions: Flags describe pointer/direct devices, unused contact dropping, in-kernel tracking, semi-MT, and total force. `struct input_mt_slot` stores ABS_MT values, frame, and key. `struct input_mt` stores next tracking id, slot count/current slot, flags, frame, reduced cost matrix, and flexible slot array. Helpers set/get slot values, test active/used slots, initialize/destroy slots, allocate tracking ids, report slot state/finger count/pointer emulation, drop unused slots, sync frames, assign slots from positions, and look up slots by key.

Control flow: Touch drivers initialize slots, report per-contact slot state and ABS_MT values each frame, call sync helpers, and optionally use assignment/tracking helpers.

State/persistence: Slot state persists across frames to maintain tracking ids and contact continuity.

Dependencies/integration: Depends on core input event reporting and ABS_MT UAPI ranges.

Risks: Failing to sync/drop unused slots leaves stale touches; incorrect slot assignment causes pointer jumps.

Test signals: Multi-finger tracking, contact add/remove/reorder, pointer emulation, semi-MT devices, and tracking-id wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/mt.h -->
