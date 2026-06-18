# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/object.h

## Purpose
Declares the core NVIF object wrapper, object lifecycle/method/map APIs, class-selection helpers, and mapped-object MMIO access macros.

## Important APIs, Types, And Functions
Defines `nvif_sclass`, `nvif_object`, `nvif_map`, constructor/destructor/ioctl/method/map/sclass APIs, `nvif_mclass`, `nvif_sclass`, MMIO `nvif_rd/wr/mask`, and DRF wrappers `NVIF_RD32/RV32/TD32/WR32/WV32/WD32/MR32/MV32/MD32`.

## Control Flow
Object construction creates child objects under a parent. Method calls use ioctl dispatch. Class matching queries supported classes then selects the first compatible requested class. Map helpers expose BAR/object mappings for MMIO-style access.

## State And Persistence
Each object stores parent, client, name, handle, class, private pointer, and optional mapping pointer/size until destruction or unmap.

## Dependencies And Integration Points
Depends on `nvif/os.h` and `nvhw/drf.h`; all NVIF wrappers embed or operate on `nvif_object`.

## Risks
Handle collisions, stale mappings, unsupported class selection, and unchecked mapped access are central risks. `priv` is marked as a hack and should not become a broad contract.

## Test Signals
Object lifecycle tests, supported-class selection, map/unmap, MMIO access, and ioctl trace logs validate behavior.
