# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_lrc_layout.h

## Purpose

`xe_lrc_layout.h` defines dword indexes inside Xe logical ring context (LRC) state and indirect context state images. It lets context setup and save/restore code address ring head/tail/start/control, context-control, timestamp, PDP, ASID, interrupt reporting, and indirect ring fields by symbolic offset.

## Important APIs, Types, and Definitions

- Main context fields: `CTX_CONTEXT_CONTROL`, `CTX_RING_HEAD`, `CTX_RING_TAIL`, `CTX_RING_START`, `CTX_RING_CTL`, `CTX_BB_PER_CTX_PTR`, `CTX_CS_INDIRECT_CTX`, `CTX_TIMESTAMP`, `CTX_ASID`, and `CTX_PDP0_*`.
- Interrupt report fields: `CTX_LRM_INT_MASK_ENABLE`, `CTX_INT_MASK_ENABLE_*`, `CTX_LRI_INT_REPORT_PTR`, `CTX_INT_STATUS_REPORT_*`, `CTX_INT_SRC_REPORT_*`, and `CTX_CS_INT_VEC_*`.
- Indirect context fields: `INDIRECT_CTX_RING_HEAD`, `INDIRECT_CTX_RING_TAIL`, `INDIRECT_CTX_RING_START`, `INDIRECT_CTX_RING_START_UDW`, and `INDIRECT_CTX_RING_CTL`.

## Control Flow

The file is pure layout metadata. Context image builders and context-restore code index into arrays of dwords using these constants when emitting LRI/LRM-style state or initializing indirect contexts.

## State and Persistence Behavior

The represented state lives in GPU context images persisted in memory and restored by hardware when contexts run. Incorrect indexes can corrupt context state across submissions or resets.

## Dependencies and Integration Points

There are no includes. The constants integrate with LRC allocation/init, engine submission, context switch save/restore, and interrupt-reporting context programming.

## Risks and Edge Cases

- Offsets include `+ 1` adjustments that reflect hardware context image conventions; removing or duplicating the adjustment would shift all state writes.
- There is no type checking on the dword array being indexed.
- Context layout varies by hardware generation; consumers must ensure these offsets match the context image they are programming.

## Test Signals

Signals include successful context creation, ring head/tail tracking, indirect context execution, interrupt reporting from contexts, and no context corruption after preemption, reset, or migration between engines.
