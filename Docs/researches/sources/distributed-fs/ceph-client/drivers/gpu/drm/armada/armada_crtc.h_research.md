# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_crtc.h

## Purpose

`armada_crtc.h` defines the Armada CRTC private structure, register-queue helpers, clock-selection data structures, and CRTC/platform-driver declarations shared by Armada DRM files.

## Important APIs, Types, And Functions

`struct armada_regs` stores one queued register update as offset, mask, and value. Macros `armada_reg_queue_mod()`, `armada_reg_queue_set()`, and `armada_reg_queue_end()` append queue entries and terminators. `struct armada_crtc` embeds `struct drm_crtc` and stores variant data, MMIO, clock, interlaced field values, cursor state, hardware config, IRQ state, deferred update/event state, and a 32-entry register queue. `struct armada_clocking_params` and `struct armada_clk_result` support clock selection. The header declares `armada_drm_crtc_update_regs()`, `armada_crtc_select_clock()`, and `armada_lcd_platform_driver`.

## Control Flow

The header has no standalone control flow. Register-queue macros are used by CRTC and plane atomic code to batch masked writes. The `armada_crtc` fields are read and mutated by CRTC IRQ, atomic, cursor, debugfs, and variant code.

## State And Persistence Behavior

The struct defines persistent per-CRTC software state, especially deferred register updates and cursor/update flags that bridge atomic commit code and IRQ handling. `atomic_regs` is stack-like per-commit state stored in the CRTC object. `event` persists until vblank delivery.

## Dependencies And Integration Points

The header depends on DRM CRTC types and forwards Armada GEM/variant types. It integrates `armada_crtc.c`, variant files, plane/overlay code, debugfs, and master driver code.

## Risks And Edge Cases

The queue macros do not bounds-check `regs_idx`; callers must ensure the 32-entry array is sufficient. The mask convention stores the inverted mask in queue entries, so misuse can write unexpected bits. `drm_to_armada_crtc()` assumes the embedded CRTC layout. Cursor object references and update callbacks must be cleared before object release.

## Test Signals

Compile coverage, register queue overflow review, atomic plane update tests that use queued registers, IRQ/event tests, cursor lifetime tests, and clock-selection unit-style coverage are useful validation signals.
