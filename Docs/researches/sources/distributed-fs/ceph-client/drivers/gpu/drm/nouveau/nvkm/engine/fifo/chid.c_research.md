<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chid.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chid.c

## Purpose

`chid.c` implements the CHID/CGID allocator used by FIFO runlists and channel groups, including event initialization and id-to-data lookup storage.

## Important APIs, Types, And Functions

`nvkm_chid_new()` allocates the flexible bitmap structure, initializes kref, mask, lock, data array, reserves ids outside the allowed range, and initializes an event source. `nvkm_chid_get()` finds the first free id, marks it used, and stores caller data. `nvkm_chid_put()` clears data under the caller's data lock and releases the bit. `nvkm_chid_ref()` and `nvkm_chid_unref()` manage lifetime; the destructor finalizes events and frees arrays.

## Control Flow

FIFO oneinit creates allocators globally or per runlist. Channel and group constructors call get. Destructors call put. Interrupt handlers use the stored data arrays through runlist helpers while respecting locks. Event notification, such as channel error, uses the allocator's event source.

## State And Persistence Behavior

The allocator persists a bitmap of used ids, a data pointer per id, a mask usually `nr - 1`, a spinlock, kref, and event object. Ids before `first` and after `first + count` are permanently reserved.

## Dependencies And Integration Points

It depends on core event helpers and is used by FIFO base, runlist, channel, channel-group, and event notification paths.

## Risks And Edge Cases

`mask = nr - 1` assumes hardware-friendly id counts, commonly powers of two. `nvkm_chid_put()` takes both allocator and data locks; callers must pass the correct lookup lock. Exhaustion returns `-1` and must become `-ENOSPC` in callers.

## Test Signals

Signals include correct id exhaustion/reuse, reserved range enforcement, channel error event delivery, no stale data pointer after put, and no use-after-free under interrupt lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chid.c -->
