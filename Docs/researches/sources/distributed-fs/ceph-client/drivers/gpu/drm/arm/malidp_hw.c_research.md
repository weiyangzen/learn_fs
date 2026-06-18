# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_hw.c

## Purpose

`malidp_hw.c` is the hardware abstraction layer for Mali-DP500, DP550, and DP650. It records per-variant layers, formats, register maps, IRQ maps, rotation-memory sizing, config-mode operations, timing programming, scaling coefficient programming, mclk validation, writeback programming, format/modifier mapping, and DE/SE IRQ handling.

## Important APIs, Types, And Functions

The file exports `malidp_device[]`, `malidp_format_modifiers[]`, `malidp_hw_get_format_id()`, `malidp_hw_format_is_linear_only()`, `malidp_hw_format_is_afbc_only()`, IRQ init/fini/hw-init helpers, and `malidp_format_get_bpp()`. Variant callbacks include `malidp500_*`, `malidp550_*`, and `malidp650_*` query, config-mode, modeset, rotmem, scaling, mclk, and memwrite functions. The internal memory-write state enum uses `MW_NOT_ENABLED`, `MW_ONESHOT`, `MW_START`, `MW_RESTART`, and `MW_STOP`.

## Control Flow

At bind time `malidp_drv.c` selects one `malidp_device[]` entry. `query_hw()` reads config registers to set min/max line size and rotation-memory banks. Modeset callbacks program output depth, background color, timing, sync polarities, interlace bit, prefetch start, and DP500 ARQOS workaround. Atomic checks call `rotmem_required()` and `se_calc_mclk()`. Commit paths call scaling coefficient callbacks and writeback enable/disable callbacks. DE IRQ handles DC config-valid completion first, sends pending events, updates the config-valid atomic, then handles vblank and error bits. SE IRQ handles scaling-engine/writeback completion and emulates one-shot writeback on DP500 by disabling memwrite after start.

## State And Persistence Behavior

The variant tables are static immutable driver data. Runtime hardware state lives in `struct malidp_hw_device`: line limits, rotation-memory sizes, output color depth, `pm_suspended`, `mw_state`, and ARQOS value. Hardware register state includes config-mode request, config-valid bit, timing, display function, scaling coefficients, memory-write pointers/strides, IRQ masks/status, and AFBC format IDs. IRQ handlers avoid MMIO when `pm_suspended` is true.

## Dependencies And Integration Points

This file depends on clocks, delays, MMIO, DRM FourCC/modifiers, vblank, Mali-DP register macros, driver private state, and writeback core. It is the central integration point between generic DRM state and variant-specific hardware programming for DP500/550/650.

## Risks And Edge Cases

Variant differences are dense: DP500 has a smaller address space, different config registers, no CLEARIRQ register, different scaling coefficient programming, one rotation-memory bank, and emulated writeback one-shot; DP550/650 share many paths but differ in line-size encodings, AFBC features, bus alignment, and rotation support. IRQ clearing differs by register-map feature. Some format IDs vary for AFBC YUYV. mclk checks only compare against current firmware-provided mclk. Memwrite state races are coordinated with config-valid IRQ state and must remain ordered.

## Test Signals

Validation should include DP500/550/650 probe, line-size and rotation-memory detection, mode timing programming, interlace programming, ARQOS on LS1028A-like systems, all supported format IDs and modifier variants, scaling coefficient changes, mclk rejection, writeback completion on DP500 and DP550/650, shared IRQ behavior while suspended, DE/SE error debugfs counters, and config-valid event wakeups.
