# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/reg.h

## Purpose
`reg.h` centralizes GVT-specific PCI, OpRegion, display, forcewake, ring-buffer, GMBUS, TRTT, and compatibility register constants not directly provided or stable in i915 headers.

## Important APIs, Types, And Functions
It defines PCI offsets, OpRegion offsets/sizes, flip-event helpers, `REG_50080` and reverse mapping macros, masked-bit helpers, forcewake offsets, ring head/tail masks, PCH GMBUS/PPS offsets, TRTT registers, `RING_EXCC`, `RING_GFX_MODE`, and `VF_GUARDBAND`.

## Control Flow
No functions are present. Statement-expression macros compute register offsets, pipe/plane identities, masked-bit states, and ring-buffer sizes.

## State And Persistence
No state is owned here. Constants define how other files interpret virtual MMIO, PCI config, and OpRegion state.

## Dependencies And Integration Points
`handlers.c`, `opregion.c`, and related GVT files consume these constants. Many macros assume i915 types and helpers such as `_MMIO`, pipe IDs, plane IDs, and masked-field helpers are visible in the including source.

## Risks
Stale constants can break OpRegion SWSCI decoding, flip event mapping, forcewake ACK handling, and ring-buffer interpretation. GNU statement-expression macros assume compatible argument types.

## Test Signals
Compile against current i915 headers, correct flip event selection, valid OpRegion sizing, forcewake ACK updates, ring-buffer size calculations, and no offset mismatches in guest-visible behavior.
