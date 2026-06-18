# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/riva_hw.h

## Purpose
`riva_hw.h` defines the RIVA hardware abstraction contract: fixed-width types, raw MMIO/VGA access macros, architecture constants, memory-mapped FIFO method object layouts, the `RIVA_HW_INST` virtual chip object, the `RIVA_HW_STATE` mode snapshot, exported low-level functions, and FIFO availability macro.

## Important APIs, types, and functions
- Access macros: `NV_WR08/16/32`, `NV_RD08/16/32`, `VGA_WR08`, and `VGA_RD08`.
- Architecture constants: `NV_ARCH_03`, `NV_ARCH_04`, `NV_ARCH_10`, `NV_ARCH_20`, `NV_ARCH_30`, `NV_ARCH_40`.
- FIFO object structs: `RivaRop`, `RivaPattern`, `RivaClip`, `RivaRectangle`, `RivaScreenBlt`, `RivaPixmap`, `RivaBitmap`, `RivaTexturedTriangle03`, `RivaTexturedTriangle05`, `RivaLine`, `RivaSurface`, and `RivaSurface3D`.
- `RIVA_HW_INST` stores hardware capabilities, MMIO pointers, function pointers, current state, and FIFO object pointers.
- `RIVA_HW_STATE` stores extended mode fields such as PLLs, repaint, arbitration, cursor, pitch, offsets, dither, scale, and two-head owner state.
- `RIVA_FIFO_FREE()` waits for and consumes FIFO slots.

## Control flow
The header has no standalone control flow, but its function pointers define the runtime dispatch model used by the driver. `RivaGetConfig()` fills `RIVA_HW_INST`; fbdev callbacks then call generic methods such as `chip->Busy()` or `chip->SetStartAddress()` without knowing the architecture. FIFO writes in `fbdev.c` are guarded by `RIVA_FIFO_FREE()`.

## State and persistence behavior
The defined structs mirror live hardware state. `RIVA_HW_INST` persists for the lifetime of the framebuffer device inside `struct riva_par`; `RIVA_HW_STATE` instances hold initial/current mode state for restore and mode switches. `RIVA_FIFO_FREE()` mutates `FifoFreeCount`, so callers must treat it as shared state tied to FIFO submissions.

## Dependencies and integration points
This header depends on `asm/io.h` and Linux `__iomem` conventions. It is included by `rivafb.h`, `fbdev.c`, `nv_driver.c`, and `riva_hw.c`. The struct layouts must match NVIDIA FIFO method offsets consumed by hardware and by table initialization in `riva_tbl.h`.

## Risks and test signals
Risks include raw `__raw_*` MMIO ordering/endian semantics, volatile struct layout assumptions, unchecked infinite FIFO waits, float fields in MMIO method structs, and architecture register layout mismatch. Test signals are compile-time sparse/checker cleanliness for `__iomem`, successful accelerated operations, no FIFO deadlocks under console stress, and correct behavior on big-endian configurations.
