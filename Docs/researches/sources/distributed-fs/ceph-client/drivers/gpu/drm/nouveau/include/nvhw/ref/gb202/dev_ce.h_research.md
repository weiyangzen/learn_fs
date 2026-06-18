# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb202/dev_ce.h

## Purpose
Defines the GB202 copy-engine GRCE mask register.

## Important APIs, Types, And Functions
Exports `NV_CE_GRCE_MASK`, `NV_CE_GRCE_MASK_VALUE`, and its init value.

## Control Flow
Declarative only. Driver code reads the mask to determine which copy-engine instances are graphics-copy-engine capable or reserved.

## State And Persistence
No C state. The register value is hardware-provided/configuration state.

## Dependencies And Integration Points
Integrated with CE discovery, runlist/engine selection, and scheduler setup for GB202.

## Risks
Treating the mask as writable or using stale assumptions about CE layout can schedule work on unsupported engines.

## Test Signals
CE enumeration, copy tests, GRCE exclusion behavior, and runlist engine masks validate usage.
