# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sa_media.h

## Purpose
`intel_sa_media.h` declares the standalone media GT setup entry point.

## Important APIs, Types, And Functions
It forward-declares `struct intel_gt` and declares `intel_sa_mediagt_setup(struct intel_gt *gt, phys_addr_t phys_addr, u32 gsi_offset)`.

## Control Flow
The header defines no runtime flow. Callers include it when platform probing needs to initialize a media GT with a physical base and GSI offset.

## State, Persistence, And Dependencies
No state is stored here. It depends on Linux integer and physical address types.

## Integration Points
The declaration connects platform/GT discovery code to `intel_sa_media.c`.

## Risks
The include guard macro name and trailing comment differ slightly, which is harmless to compilation but worth noting for consistency. API misuse mainly means passing an uninitialized `intel_gt` or incorrect GSI offset.

## Test Signals
Compile coverage and probe coverage on standalone media platforms validate the header contract.
