# sources/distributed-fs/ceph-client/lib/crypto/arm64/sm3.h

## Purpose
ARM64 SM3 dispatch header selecting CE, NEON, or generic SM3 compression.

## Important APIs, Types, And Functions
Declares `sm3_neon_transform` and `sm3_ce_transform`, defines static keys `have_neon` and `have_ce`, overrides `sm3_blocks()`, and provides `sm3_mod_init_arch()`.

## Control Flow
When ASIMD is enabled and SIMD is usable, `sm3_blocks()` enters `scoped_ksimd()` and picks CE if `have_ce` is enabled, otherwise NEON. If ASIMD or SIMD context is unavailable, it calls `sm3_blocks_generic()`. Init enables ASIMD and then the SM3 CE key when CPU features allow.

## State, Persistence, And Dependencies
Caller-owned block state is the only mutable hash state. Static keys are global feature flags initialized once. Dependencies are CPU feature detection and kernel SIMD helpers.

## Integration Points
Used by the generic SM3 crypto library for arm64 acceleration and by higher-level consumers needing SM3 hashes.

## Risks
CE and NEON availability are separate: SM3 CE requires ASIMD wrapping too. A dispatch bug can either fault on unsupported instructions or miss acceleration. Generic fallback is required in non-SIMD contexts.

## Test Signals
Feature matrix tests, forced generic/NEON/CE paths, and SM3 known-answer vectors through streaming APIs verify the wrapper.
