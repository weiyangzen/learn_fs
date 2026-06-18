# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-mailbox.h

## Purpose
This header declares the ivtv firmware mailbox API and names the DMA mailbox slots.

## Important APIs, Types, and Functions
It defines `IVTV_MBOX_DMA_END` and `IVTV_MBOX_DMA`, and declares the command helpers `ivtv_api`, `ivtv_vapi_result`, `ivtv_vapi`, `ivtv_api_func`, `ivtv_api_get_data`, and `ivtv_mailbox_cache_invalidate`.

## Control Flow
There is no executable logic. Callers use fixed mailbox slots for IRQ-side DMA data extraction and use the helper functions for sleepable firmware commands.

## State and Persistence Behavior
The header stores no state. The declared functions manipulate firmware mailbox memory, command cache timestamps, and mailbox busy bits.

## Dependencies and Integration Points
It depends on `struct ivtv`, `struct ivtv_mailbox_data`, CX2341x mailbox data sizing, and `u32`. It is included by ioctl, stream lifecycle, IRQ, framebuffer, and other firmware-control modules.

## Risks
The DMA slot constants must match firmware layout. `ivtv_api_get_data` is intended for non-sleeping contexts, so callers must not replace it with the sleepable API in IRQ paths.

## Test Signals
Build coverage for all users and runtime testing of DMA interrupt data, OSD calls, encoder/decoder start/stop, and firmware cache invalidation cover this interface.
