# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_intr.h

## Purpose
This header exposes the shared vcodec interrupt wait helper and the interrupt-received reason bit.

## Important APIs, Types, And Functions
`MTK_INST_IRQ_RECEIVED` marks a normal hardware completion interrupt. `mtk_vcodec_wait_for_done_ctx()` waits on a decoder or encoder context for a command to finish on a selected hardware index. Decoder and encoder context structs are forward-declared.

## Control Flow
No direct execution. Hardware interrupt handlers wake context queues with this reason; codec workers call the declared helper to wait for completion.

## State, Persistence, And Dependencies
No state in the header. It depends on context definitions at implementation call sites and the common wait implementation.

## Integration Points
Included by decoder parent/subdevice drivers, PM/hardware code, and codec-specific interface files.

## Risks
The API uses `void *priv`, so type safety is weak and depends on caller discipline. The `hw_id` parameter must be valid for the context's arrays.

## Test Signals
Compile coverage from decoder and encoder code and runtime interrupt wait coverage for each hardware index.
