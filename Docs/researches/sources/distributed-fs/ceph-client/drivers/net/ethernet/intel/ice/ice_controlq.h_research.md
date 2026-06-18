# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_controlq.h

## Purpose
`ice_controlq.h` defines the control queue ABI used by `ice_controlq.c` and all AQ callers. It supplies maximum command buffer sizes, descriptor ring access macros, expected firmware API versions, queue type identifiers, timeout constants, and the per-ring/per-queue state structures used for AdminQ, mailbox, and sideband queues.

## Important APIs, Types, And Functions
The key macros are `ICE_CTL_Q_DESC(R, i)` for descriptor lookup and `ICE_CTL_Q_DESC_UNUSED(R)` for ring space accounting. Expected firmware AdminQ API version macros distinguish E810-compatible and E830-compatible devices through `EXP_FW_API_VER_MAJOR_BY_MAC()` and `EXP_FW_API_VER_MINOR_BY_MAC()`.

`enum ice_ctl_q` names software queue roles: unknown, AdminQ, mailbox, and sideband. `struct ice_ctl_q_ring` holds descriptor DMA memory, per-entry DMA buffer arrays, ring cursor values, queue count, and MMIO register offsets/masks. `struct ice_sq_cd` carries optional send command details, currently only a writeback descriptor pointer. `struct ice_rq_event_info` is the receive-event handoff container. `struct ice_ctl_q_info` aggregates the send and receive rings, configured queue depths and buffer sizes, last send status, and mutexes.

## Control Flow
The header does not implement control flow but shapes it. Initialization code fills `num_*_entries` and `*_buf_size`, then `ice_controlq.c` populates register offsets and DMA fields. Send paths use `ICE_CTL_Q_DESC_UNUSED()` after cleaning to determine space, then index descriptors with `ICE_CTL_Q_DESC()`. Receive paths fill `ice_rq_event_info` before handing events to upper layers.

## State And Persistence
All structures are in-memory driver state mirrored partly into hardware queue registers. The descriptor buffers and per-entry indirect buffers are DMA-coherent memory. The header itself defines no persistent storage, but its queue state must survive runtime command submission until explicit queue shutdown or driver removal.

## Dependencies And Integration Points
It includes `ice_adminq_cmd.h` for `struct libie_aq_desc` and firmware status enums. It is included by queue code and indirectly by most firmware-command modules. The buffer size constants (`ICE_AQ_MAX_BUF_LEN`, `ICE_MBXQ_MAX_BUF_LEN`, `ICE_SBQ_MAX_BUF_LEN`) define limits that callers and queue setup must respect.

## Risks
The descriptor-unused macro assumes consistent ring cursor management and one unused descriptor slot. Incorrect queue depth or buffer size initialization leads to `-EIO` during queue init. Firmware API constants gate device load behavior, so updates to supported NVM/firmware combinations must keep these macros synchronized with firmware compatibility policy.

## Test Signals
Compile coverage across `CONFIG_*` variants, successful AdminQ version validation on E810/E830 families, queue depth boundary tests, indirect buffer-size rejection, and reset/reinit cycles are the best signals that these definitions still match the implementation and firmware contract.
