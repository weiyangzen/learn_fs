# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_crtc.c

## Purpose

`armada_crtc.c` implements the Marvell Armada LCD CRTC component driver. It handles register-queue updates, timing programming including interlaced-field fixups, IRQ/vblank/event handling, gamma SRAM programming, hardware cursor management, clock selection support, CRTC creation/destruction, and LCD component/platform driver registration.

## Important APIs, Types, And Functions

Exported APIs are `armada_drm_crtc_update_regs()`, `armada_crtc_select_clock()`, and `armada_lcd_platform_driver`. Major internal functions include `armada_drm_crtc_mode_set_nofb()`, atomic check/begin/flush/enable/disable helpers, IRQ helpers, cursor set/move/update/load helpers, `armada_drm_crtc_create()`, and component bind/unbind/probe routines. `struct armada_regs` queues masked register writes used by atomic plane/CRTC paths.

## Control Flow

LCD platform probe registers a component. Bind maps MMIO, allocates `struct armada_crtc`, initializes registers and IRQ state, requests the IRQ, runs variant init, creates the primary plane and CRTC, enables color management, and creates overlay planes. Mode fixup validates mode flags and asks the variant to validate clocking. Mode-set computes real SCLK, prepares per-field interlaced timing values, queues timing/polarity registers, and writes them under `irq_lock`. Atomic begin handles gamma changes and starts a register queue. Atomic flush terminates the queue and either applies immediately for modesets or defers to `DUMB_FRAMEDONE` IRQ for active updates, arming events as needed. IRQ handles underflows, vblank, interlaced field register swaps, deferred register application, cursor updates, and event delivery.

## State And Persistence Behavior

`struct armada_crtc` stores CRTC number, MMIO base, selected clock, interlace field register snapshots, cursor object/position/size, dumb/io-pad config, IRQ enable mask, pending update/event flags, and atomic register queue. Hardware state persists in LCD SPU timing, DMA, SRAM, cursor, IRQ, and clock registers. Cursor GEM objects can call back into `cursor_update()` after CPU writes.

## Dependencies And Integration Points

The file depends on DRM atomic/vblank helpers, component framework, OF/platform matching, Armada fb/GEM/plane/overlay/hardware headers, tracepoints, and variant callbacks from `armada_510.c`. It integrates with `armada_drv.c` as a child component bound into the master DRM device.

## Risks And Edge Cases

Interlaced modes require per-field register rewrites on graphics frame IRQs and an extra vblank reference. Deferred register queues have a fixed 32-entry array; plane code must not overflow it. Event delivery waits until updates are no longer pending. Cursor SRAM has unusual ABGR packing and size limits. IRQ enable/disable is protected by `irq_lock`, and incorrect masking can lose vblank or frame-done events. Mode validation rejects vscan/doublescan/hskew and interlace without advanced register support.

## Test Signals

Validation should cover progressive and interlaced modes, frame-done deferred updates, vblank/page-flip events, gamma LUT size and SRAM programming, cursor set/move/cropping/reload, underflow logging, clock selection boundaries, component bind/unbind, overlay/primary plane register queue interactions, and debugfs register visibility.
