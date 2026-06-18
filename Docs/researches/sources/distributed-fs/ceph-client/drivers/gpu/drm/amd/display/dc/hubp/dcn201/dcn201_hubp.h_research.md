# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn201/dcn201_hubp.h

Purpose: declares the DCN201 HUBP register/field subset and concrete object. It captures a hybrid hardware surface: based on DCN common registers, with prefetch settings, cursor0, DMDATA, triple-buffer, vready, and limited flip-parameter support.

Important APIs and types: `TO_DCN201_HUBP` casts from `hubp`. `HUBP_REG_LIST_DCN201` defines the DCN201 register set, including common DCN registers, prefetch, flip control2, cursor registers, DMDATA registers, and selected flip parameters. `HUBP_MASK_SH_LIST_DCN201` defines fields, including DCN common fields, cursor fields, DMDATA fields, triple-buffer, vready, disable-stop-data-during-VM, and master update lock status. `struct dcn201_hubp_registers`, `struct dcn201_hubp_shift`, `struct dcn201_hubp_mask`, and `struct dcn201_hubp` provide the concrete register metadata and object. `dcn201_hubp_construct` is the exported constructor.

Control flow role: the header enables a narrow C implementation to bind DCN201-specific register tables while reusing DCN1/DCN2 helper functions. Its macro lists determine which shared helper calls can safely access registers on this ASIC.

State and persistence behavior: `struct dcn201_hubp` embeds common `struct hubp` and shared `dcn_hubp_state`; no extra persistent fields are introduced. State behavior therefore follows delegated DCN1/DCN2 helpers.

Dependencies and integration points: includes both `dcn10_hubp.h` and `dcn20_hubp.h`, making it an explicit bridge generation. Resource construction code supplies `dcn201_hubp_registers`, shifts, and masks.

Risks: the register list lacks some full DCN2 fields, so assigning a DCN2 helper that touches absent registers would be unsafe. Field-list omissions can break DMDATA or flip timing silently. The include guard closing comment references DCN20, which is cosmetic but can confuse maintenance.

Test signals: build-time register initialization for DCN201, plus runtime DMDATA, cursor, prefetch, triple-buffer, vready, and flip register tests on DCN201 hardware or register-model tests.
