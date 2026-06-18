# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn401/dcn401_hubp.h

Purpose: declares the DCN 4.0.1 HUBP register/mask inventory and public functions. It bridges legacy HUBP infrastructure to DML2 DCHUB register payloads and adds 3D LUT fast-load and MCACHE fields.

Important APIs and definitions: `HUBP_3DLUT_FL_REG_LIST_DCN401()` lists 3D LUT fast-load registers. `HUBP_MASK_SH_LIST_DCN401()` enumerates DCN4 HUBP fields, including inherited surface/cursor/DLG/TTU/VM fields, MALL prefetch fields, 3D LUT fields, viewport MCACHE split, MCACHE ID config, read-line, and DET allocation status. Prototypes cover setup, interdependent setup, flip/address programming, DCC, tiling, size, surface config, viewport, MCACHE, flip interrupt, blank, cursor position, read state, construct, init, 3D LUT helpers, clear tiling, vready/vsync, requestor, and deadline programming.

Control flow: declaration-only, but it defines which functions can be placed in DCN4 `hubp_funcs`. `hubp401_setup()` consumes `struct dml2_dchub_per_pipe_register_set`, global sync programming, and timing, making it a key interface between DML2 calculations and register programming.

State and persistence: the mask list covers all persistent hardware state written by `dcn401_hubp.c`: plane addresses, formats, DCC, tiling, pstate/MALL, DLG/TTU timing, VM settings, 3D LUT DMA, MCACHE, and diagnostics. The header also pulls in DML2 register definitions, so type compatibility is part of the ABI inside Display Core.

Dependencies and integration points: includes DCN 2.0/2.1/3.0/3.1/3.2 HUBP headers and DML2 DCHUB register definitions. It is included by `dcn42_hubp.c` for reused DCN4 helpers. Integration points include color management, DML2, HWSS, resource construction, and register table generation.

Risks and test signals: the macro is large and generation-specific, so register-spec drift is likely during bring-up. Some fields from earlier DCN3 meta programming are intentionally reduced or changed for DCN4, and consumers must not assume old DCC/meta behavior. Signals include compile coverage for generated tables, DML2 modeset tests, 3D LUT fast-load tests, MCACHE/MALL scenarios, and per-register readback validation.
