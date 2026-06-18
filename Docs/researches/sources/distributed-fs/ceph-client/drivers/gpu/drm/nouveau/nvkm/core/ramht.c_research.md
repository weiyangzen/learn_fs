## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/ramht.c

### Purpose
`ramht.c` implements Nouveau's RAMHT handle table helper for older FIFO/channel hardware. It stores channel/handle to GPU object instance bindings in both CPU-side metadata and a GPU object backing table.

### Important APIs, types, and functions
The API consists of `nvkm_ramht_new()`, `nvkm_ramht_del()`, `nvkm_ramht_insert()`, `nvkm_ramht_remove()`, and `nvkm_ramht_search()`. Internal helpers are `nvkm_ramht_hash()` and `nvkm_ramht_update()`. State is held in `struct nvkm_ramht` and `struct nvkm_ramht_data`.

### Control flow
`nvkm_ramht_new()` allocates a variable-sized CPU table, initializes every entry with `chid = -1`, computes hash bits from entry count, and allocates the GPU object backing store. Insert rejects duplicate channel/handle pairs, probes linearly from the XOR hash, binds the object into a small context GPU object when supported, computes the instance address for pre/post NV50 hardware, writes handle/context dwords into the RAMHT GPU object, and returns a one-based cookie. Remove converts the cookie back to an index and clears the entry via `nvkm_ramht_update()` with no object.

### State and persistence behavior
Entries persist in `ramht->data` and in the GPU object until removed or the whole table is deleted. Per-entry bound instance GPU objects are destroyed before replacement. The table does not compact or rehash; deletion marks slots empty by setting `chid = -1`.

### Dependencies
The file depends on `core/ramht.h`, `core/engine.h`, `core/object.h`, GPU object allocation/map/write helpers, `order_base_2()`, `vzalloc()`, and `vfree()`.

### Integration points
FIFO/channel setup uses RAMHT entries to let hardware resolve object handles to engine contexts. It integrates with `nvkm_object_bind()` so engine object classes can provide hardware-specific context records.

### Risks
Hash/probe behavior depends on table size being a power-of-two-compatible byte size. The `addr` argument shifts instance addresses into caller-specified context fields; wrong values corrupt RAMHT entries. The code has no internal lock, so channel/object management must serialize access. Binding returns `-ENODEV` for objects with no bind callback and is treated as a valid unbound object, which callers must expect.

### Test signals
Exercise duplicate insert, full-table `-ENOSPC`, search after wraparound probing, remove/reinsert of the same slot, engine objects with and without bind callbacks, and hardware channel creation on G8x/NV50-era GPUs.
