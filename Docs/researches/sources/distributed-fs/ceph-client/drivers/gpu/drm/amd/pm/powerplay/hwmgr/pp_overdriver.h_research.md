# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_overdriver.h

## Purpose
`pp_overdriver.h` declares the tiny public interface for Vega overdrive default fuse lookup. It defines the record shape consumed by `pp_overdriver.c` and exported to ASIC-specific hwmgr code.

## Important APIs and types
The main type is `struct phm_fuses_default`, with a 64-bit lookup `key` and three voltage/frequency transfer coefficient groups: `VFT2_m1/m2/b`, `VFT1_m1/m2/b`, and `VFT0_m1/m2/b`. The only function prototype is `pp_override_get_default_fuse_value(uint64_t key, struct phm_fuses_default *result)`.

## Control flow and state
This header has no executable code and no persistent state. It carries include guards, includes Linux integer/kernel definitions, and exposes the struct/function contract used by `pp_overdriver.c`.

## Dependencies and integration points
Consumers include this header when they need fallback fuse coefficients, notably Vega10 power management. The header depends only on standard kernel integer definitions and does not pull in hwmgr state, which keeps it isolated from broader powerplay internals.

## Risks and test signals
The ABI risk is field ordering: callers expect exact names and sizes when copying table records. Because the implementation does field-by-field copies rather than struct assignment, adding fields would require updating `pp_override_get_default_fuse_value()`. Build coverage should catch prototype mismatches; functional coverage needs the `.c` lookup tests.
