# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn42/dcn42_mmhubbub.h

Purpose: declares the DCN4.2 MMHUBBUB FGC clock-gating helper.

Important API: `dcn42_mmhubbub_set_fgcg(struct dcn30_mmhubbub *mcif_wb30, bool enabled)`.

Control flow/state: no state in the header; callers pass a DCN30-style MMHUBBUB object with DCN4.2/DCN35-compatible register metadata.

Dependencies/integration: includes `mcif_wb`, DCN32, and DCN35 MMHUBBUB headers so the implementation can reuse inherited types and register layout.

Risks: no constructor is declared here, so object setup must come from resource code or inherited constructors. Header guard is present but lacks a trailing double underscore convention, matching nearby DCN35 style.

Test signals: build coverage for DCN4.2 resource code and runtime FGC register updates.
