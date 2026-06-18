# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_hw.h

## Purpose

`malidp_hw.h` defines the Mali-DP hardware abstraction contract used by the rest of the driver. It describes block IDs, layer IDs, format IDs, IRQ maps, layer register metadata, scaling-engine configuration, register-map features, variant callback tables, runtime hardware-device state, MMIO helpers, IRQ helper prototypes, format helper prototypes, pitch-alignment/scaling helpers, and AFBC modifier constants.

## Important APIs, Types, And Functions

Key types include `struct malidp_format_id`, `struct malidp_irq_map`, `struct malidp_layer`, `struct malidp_se_config`, `struct malidp_hw_regmap`, `struct malidp_hw`, and `struct malidp_hw_device`. Inline helpers include `malidp_hw_read()`, `malidp_hw_write()`, `malidp_hw_setbits()`, `malidp_hw_clearbits()`, `malidp_get_block_base()`, IRQ enable/disable helpers, `malidp_hw_get_pitch_align()`, `malidp_se_select_coeffs()`, and `malidp_se_set_enh_coeffs()`.

## Control Flow

The header does not own top-level control flow but defines callback entry points used during probe, atomic check, commit, modeset, writeback, and IRQ setup. The `struct malidp_hw` callback table lets common DRM code call variant-specific `query_hw`, config-mode, modeset, rotation-memory, scaling, mclk, and memwrite functions without switch statements.

## State And Persistence Behavior

`struct malidp_hw_device` records mutable hardware runtime state: chosen variant, MMIO, APB/AXI/main/pixel clocks, min/max line sizes, output color depth, PM suspend flag, memory-write state, rotation-memory bank sizes, and ARQOS. Inline MMIO helpers warn on access while suspended but still perform the access. Scaling and AFBC constants define hardware programming values that persist in registers after writes.

## Dependencies And Integration Points

The header depends on bitops and `malidp_regs.h`, plus DRM AFBC modifier definitions available through included driver paths. It integrates all Mali-DP implementation files and exposes `malidp_device[]` and `malidp_format_modifiers[]` to the probe and plane/framebuffer validation paths.

## Risks And Edge Cases

The callback table is a hardware ABI inside the driver; a missing callback can break probe or commit paths. `malidp_hw_get_pitch_align()` increases alignment for rotated planes only on devices with bus alignments above 8 bytes. `malidp_se_select_coeffs()` uses fixed U16.16 threshold comparisons and must match coefficient table indexing. `malidp_se_set_enh_coeffs()` computes an offset differently depending on CLEARIRQ feature, so register-map feature flags must stay correct.

## Test Signals

Build coverage across all Mali-DP variants, runtime PM warnings for MMIO while suspended, pitch-alignment tests for rotated/unrotated DP650 planes, scaling coefficient selection boundaries, enhancer coefficient programming, IRQ enable/disable register writes, and format modifier enumeration are useful signals.
