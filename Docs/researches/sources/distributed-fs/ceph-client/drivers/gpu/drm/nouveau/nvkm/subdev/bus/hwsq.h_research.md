<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/hwsq.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/hwsq.h

### Purpose

Header-only helper API for a newer structured hardware-sequencer builder. It defines register descriptors and inline operations for composing register reads, writes, masks, waits, and delays.

### Important APIs, types, and functions

Defines `struct hwsq`, `struct hwsq_reg`, `hwsq_reg()`, `hwsq_stride()`, `hwsq_reg2()`, and inline helpers for register write/mask/read-style operations over an abstract `struct hwsq` backend.

### Control flow

There is no standalone runtime flow. Callers construct `hwsq_reg` descriptors and invoke inlines that delegate to function pointers in `struct hwsq` or apply register address arithmetic.

### State and persistence behavior

No storage is allocated by the header. It describes transient command-building state owned by the caller/backend.

### Dependencies and integration points

Depends on basic kernel integer types. It integrates with bus/display code that wants a typed HWSQ abstraction rather than the older bytecode emitter API.

### Risks

Inline address arithmetic must preserve stride/index semantics. Because this is a header, API mistakes propagate at compile time across all users.

### Test signals

Source read size: 148 lines, 2601 bytes. Compile coverage for all HWSQ users, generated command trace comparison, and tests for stride/indexed register helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/hwsq.h -->
