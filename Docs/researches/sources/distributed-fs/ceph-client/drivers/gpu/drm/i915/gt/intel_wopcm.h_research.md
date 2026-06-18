# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_wopcm.h

## Purpose
`intel_wopcm.h` defines the WOPCM state structure and accessors for GuC WOPCM base and size.

## Important APIs, Types, And Functions
`struct intel_wopcm` stores total WOPCM `size` and nested GuC region `base` and `size`. Inline accessors `intel_wopcm_guc_base()` and `intel_wopcm_guc_size()` return zero when GuC is not present or not in use. It declares early and full initialization functions.

## Control Flow
Callers initialize the structure early, then call full init after firmware upload sizes are known. Later GuC setup reads the accessors to program or validate WOPCM registers.

## State, Persistence, And Dependencies
The structure is GT-owned in-memory state. It depends only on Linux integer types in the header.

## Integration Points
GT microcontroller initialization, GuC firmware upload, HuC reservation checks, and WOPCM register programming include this header.

## Risks
Zero is both the default and the "not in use" accessor result, so callers must ensure initialization succeeded before relying on a nonzero GuC region. The header intentionally hides layout math in the C file.

## Test Signals
Compile coverage, GuC/HuC firmware boot tests, and assertions that accessors match programmed WOPCM registers are useful signals.
