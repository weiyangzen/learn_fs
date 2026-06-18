<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chid.h

## Purpose

`chid.h` defines the FIFO channel-id allocator structure and API.

## Important APIs, Types, And Functions

`struct nvkm_chid` contains a kref, id count, mask, event source, id-to-data array, spinlock, and flexible used bitmap. The header declares create/ref/unref/get/put helpers.

## Control Flow

FIFO setup creates allocators. Channel/group creation gets ids, interrupt lookup reads data, and destruction puts ids. Event users subscribe to `chid->event`.

## State And Persistence Behavior

Persistent state is the used bitmap, data array, event object, and kref. The mask is used by hardware status decoding paths to bound CHID values.

## Dependencies And Integration Points

It includes `core/event.h` and is consumed by FIFO base, runlists, channels, and groups.

## Risks And Edge Cases

The flexible array allocation must match `nr`. Callers must not use an id after `put` clears its data pointer. Non-power-of-two `nr` values may make `mask` unsuitable for some hardware decodes.

## Test Signals

Build coverage, CHID allocation/release, event delivery, and interrupt lookup correctness validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chid.h -->
