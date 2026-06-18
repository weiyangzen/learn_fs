# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/octeon-model.c

## Purpose
Decodes Octeon chip IDs, fuses, core counts, cache fuses, and clock rate into model strings and feature flags.

## Important APIs, Types, And Functions
Exports `__octeon_feature_bits`; public API is `octeon_model_get_string(uint32_t chip_id)`. Internal helpers are `cvmx_fuse_read_byte()` and `octeon_model_get_string_buffer()`.

## Control Flow
The decoder reads fuse registers, infers disabled engines and suffix class, sets crypto feature presence, derives pass and core-model strings with family-specific exceptions, switches on family code, optionally reads model override fuses, then formats `CN...p...-MHz-suffix`.

## State, Persistence, And Dependencies
Feature bits persist globally. The public model function returns a static buffer. Dependencies include fuse command CSRs, core count, clock rate, and model predicates.

## Integration Points
Early platform diagnostics and feature checks rely on the model string and crypto feature bit.

## Risks
The static return buffer is overwritten on each call. Fuse reads spin without timeout. New families require careful table updates.

## Test Signals
Check known chip IDs, pass-number exceptions, crypto fuse feature bits, fuse model overrides, and no hangs reading fuse status.
