# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_opp.h

## Purpose
Defines the DCN201 output pixel processor register map, concrete object, and constructor.

## Important APIs, Types, And Functions
`OPP_REG_LIST_DCN201` combines DCN10 OPP registers, DPG registers, and `FMT_422_CONTROL`. `OPP_MASK_SH_LIST_DCN201` and `OPP_DCN201_REG_FIELD_LIST` reuse DCN20 fields. Types include `dcn201_opp_shift`, `dcn201_opp_mask`, `dcn201_opp_registers`, and `dcn201_opp`. `TO_DCN201_OPP()` converts from base object.

## Control Flow
No executable flow. The header supplies register descriptors for inherited OPP helper functions.

## State And Persistence
`struct dcn201_opp` stores the common output pixel processor, descriptors, and `is_write_to_ram_a_safe`. Hardware state is represented by OPP/FMT/DPG registers.

## Dependencies And Integration Points
Includes `dcn20/dcn20_opp.h`, and is used by DCN201 OPP implementation and resource construction.

## Risks
Reusing DCN20 mask fields with DCN201 register lists assumes exact compatibility. The `is_write_to_ram_a_safe` field is present but not initialized in the constructor in this subset, so users must not assume a default unless zero-initialized allocation is guaranteed.

## Test Signals
Compile-time macro expansion, OPP format programming, DPG operation, and register readback for FMT_422 and inherited OPP fields.
