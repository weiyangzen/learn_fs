# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/accel.c

## Purpose
`accel.c` initializes and drives VIA Unichrome 2D acceleration resources: hardware bitblt, virtual queue setup, cursor memory reservation, cursor visibility, and engine-idle synchronization.

## Important APIs, Types, And Functions
Exports within the VIA driver are `viafb_setup_engine()`, `viafb_reset_engine()`, `viafb_show_hw_cursor()`, and `viafb_wait_engine_idle()`. Internal helpers `hw_bitblt_1()` and `hw_bitblt_2()` program older and newer 2D register layouts, while `viafb_set_bpp()` writes GEMODE bpp bits. The implementation relies on shared `viafb_par`, `viafb_shared`, chip information, `engine_mmio`, and `hw_bitblt` function pointer state.

## Control Flow
Engine setup validates MMIO, selects the proper bitblt implementation by graphics chip generation, reserves tail framebuffer memory for cursor and virtual queue, optionally reserves camera framebuffer memory, then resets the engine. Bitblt validates operation, bpp, coordinates, dimensions, pitch, and address alignment, sets direction bits for overlapping framebuffer copies, writes source/destination/dimension/color/pitch registers, starts the blit command, and streams system-memory source data through the MMIO blit aperture if needed. Reset clears engine registers, initializes AGP/transaction and virtual queue registers with generation-specific sequences, and programs cursor base registers.

## State And Persistence
State persists in `viapar->shared`: selected `hw_bitblt` function, cursor and VQ VRAM addresses, camera offsets, and chip information. Hardware state persists in engine MMIO registers until reset or modeset. `fbmem_free` and `fbmem_used` are mutated to reserve memory regions.

## Dependencies And Integration Points
It depends on `accel.h` register definitions, `chip.h` chip IDs, `via-core` MMIO mapping, and shared VIA fbdev structures from `global.h`/`viafbdev.h`. It is called by the main VIA fbdev setup path and supports higher-level accelerated drawing/cursor code.

## Risks
The bitblt functions reject unsupported alignment and size encodings but do not recover from all hardware hangs. Engine reset sequences are magic-number heavy and chip-generation-specific. Memory reservation is a simple top-of-framebuffer subtraction without a general allocator, so feature additions can collide if ordering changes. `viafb_wait_engine_idle()` busy-waits up to `MAXLOOP` and only logs on timeout.

## Test Signals
Signals include successful acceleration setup with a non-NULL `hw_bitblt`, correct framebuffer memory accounting, cursor memory not overlapping visible buffers, bitblt fill/copy/mono operations across supported bpp values, timeout-free idle waits, and chip-matrix testing for H2, H5, and M1 engine variants.
