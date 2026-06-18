# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn35/dcn35_mmhubbub.c

Purpose: adapts the DCN3.2 MMHUBBUB implementation for DCN3.5 and adds fine-grain clock-gating control.

Important APIs/functions: `dcn35_mmhubbub_construct` delegates to `dcn32_mmhubbub_construct` with casts from DCN3.5 register/mask/shift structures to DCN3.0-compatible base structures. `dcn35_mmhubbub_set_fgcg` writes `MMHUBBUB_FGCG_REP_DIS` with the inverse of the requested enable state.

Control flow: construction is inherited; no new writeback buffer or arbitration function table is created. FGC gating is a direct register update through DCN3.5 typed register macros.

State/persistence: stores the same `dcn30_mmhubbub` base state as DCN32. FGC gating persists in `MMHUBBUB_CLOCK_CNTL`.

Dependencies/integration: includes `dcn35_mmhubbub.h` and `reg_helper`; depends on DCN32 compatibility for all MCIF operations.

Risks: the cast-based constructor assumes DCN3.5 register structures are layout-compatible with DCN3.0/DCN3.2 expectations plus appended fields. Misordered macro fields would break inherited operations.

Test signals: DCN3.5 writeback construction, inherited writeback capture, and toggling FGC gating while checking `MMHUBBUB_CLOCK_CNTL`.
