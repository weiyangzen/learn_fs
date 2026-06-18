# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn201/dcn201_hubp.c

Purpose: implements the DCN2.0.1 HUBP variant by composing DCN1 and DCN2 helpers behind a dedicated `hubp_funcs` table. It is a compatibility layer for hardware that has DCN2-style DMDATA/triple-buffer bits but lacks some full DCN2 requestor/PTE programming.

Important APIs and functions: `dcn201_hubp_construct` installs `dcn201_hubp_funcs`. Private wrappers are `hubp201_program_surface_config`, `hubp201_program_deadline`, `hubp201_program_requestor`, and `hubp201_setup`. The vtable maps many operations to DCN1 helpers (`hubp1_program_surface_flip_and_addr`, `hubp1_is_flip_pending`, `hubp1_set_blank`, DCC, viewport, clock, VTG, clear underflow, init, clear tiling) while using DCN2 helpers for setup interdependent timing, cursor attributes, DMDATA, triple-buffer, GSL, and read state.

Control flow: setup calls the DCN2 vready calculation, then the DCN201 requestor writer, then DCN1 deadline programming. The custom requestor writer programs DET buffer base and expansion modes but intentionally writes only chunk/min/meta/swath fields and comments that PTE programming is unnecessary. Surface config uses DCN1 tiling, size, pixel format, and DCC, and ignores rotation/horizontal mirror in this wrapper.

State and persistence behavior: constructor initializes base context, register metadata, instance id, invalid OPP, and disconnected MPCC. Runtime state persistence is inherited from called DCN1/DCN2 helpers: request address, cursor state, DMDATA state, and `dcn_hubp_state` readback.

Dependencies and integration points: includes both DCN10 and DCN20 headers through `dcn201_hubp.h`. It depends on the DCN201-specific register/field structs while delegating most behavior to shared DCN1/DCN2 functions. It integrates with common resource construction through `dcn201_hubp_construct`.

Risks: function composition is easy to misread: this variant uses DCN1 address flips with no VMID programming but DCN2 DMDATA and triple-buffer support. `hubp201_program_surface_config` accepts rotation and mirror parameters but does not call a rotation helper. Requestor programming omits PTE fields by design, so using a full DCN2 expectation would be wrong. Mixed DCN1 cursor position with DCN2 cursor attributes can regress if cached cursor state semantics diverge.

Test signals: run DCN201-specific modeset/plane tests that verify requestor fields exclude PTE programming, DMDATA works, triple-buffer toggles, flips use the expected DCN1 address path, and rotation/mirror behavior matches hardware support expectations.
