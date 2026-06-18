# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/yellow_carp_ppt.h

## Purpose
Declares the Yellow Carp SMU13 PPT backend setup function.

## Important APIs, Types, And Functions
- The header exports `yellow_carp_set_ppt_funcs(struct smu_context *smu)`.
- The include guard is `__YELLOW_CARP_PPT_H__`.

## Control Flow
The platform selection code calls `yellow_carp_set_ppt_funcs` for Yellow Carp-class APUs. The implementation installs APU-specific `pptable_funcs`, message mappings, feature mappings, table mappings, and driver interface version.

## State And Persistence
The header itself stores no state. Its entry point mutates `struct smu_context`, including `ppt_funcs`, `feature_map`, `table_map`, `is_apu`, and message-control setup.

## Dependencies And Integration Points
It depends on the SWSMU context type from common headers and links Yellow Carp platform selection to the implementation in `yellow_carp_ppt.c`.

## Risks And Edge Cases
Calling this setup function for the wrong firmware family would install Yellow Carp message IDs against incompatible PMFW. Header/implementation mismatch would fail compilation or platform setup.

## Test Signals
Build should compile callers and implementation with the same prototype. Runtime probe should show `is_apu` set and Yellow Carp mappings installed for the correct IP revisions.
