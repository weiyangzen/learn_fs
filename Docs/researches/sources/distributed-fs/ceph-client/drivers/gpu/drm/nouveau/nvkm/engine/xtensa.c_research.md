# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/xtensa.c

## Purpose
Implements a generic Xtensa-backed engine wrapper used by VP-like engines. It loads firmware into instance memory, programs engine memory regions, handles interrupts, and exposes engine classes.

## Important APIs, types, and functions
`nvkm_xtensa_new_()` constructs the engine. `nvkm_xtensa_init()` loads `nouveau/nv84_xuc%03x`, allocates firmware memory, writes firmware words, and programs region registers. `nvkm_xtensa_fini()` disables interrupts/FIFO and frees firmware on poweroff. `nvkm_xtensa_intr()` clears interrupts and enables FIFO control after a specific engine-ready state. `nvkm_xtensa_cclass_bind()` allocates channel context objects.

## Control flow, state, and persistence
The firmware image is cached in `xtensa->gpu_fw` until poweroff. Init programs interrupt masks, region base/limit/setup, scratch state, and engine constants. Interrupt handling reports watchdog hangs and toggles FIFO control when readiness registers match expected values.

## Dependencies and integration points
Depends on firmware loading, instance memory, GPU objects, FIFO class binding, and chip-specific `nvkm_xtensa_func`. Used by `engine/vp/g84.c`.

## Risks and test signals
Firmware size is capped at `0x40000`; missing firmware prevents init. Signals include firmware load warnings, watchdog interrupt logs, FIFO_CTRL enable debug logs, and successful class/context binding.
