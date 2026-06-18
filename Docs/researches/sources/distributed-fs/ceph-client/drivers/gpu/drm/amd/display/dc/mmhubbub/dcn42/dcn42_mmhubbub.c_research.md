# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn42/dcn42_mmhubbub.c

Purpose: provides DCN4.2 MMHUBBUB fine-grain clock-gating control using the DCN3.5 register layout.

Important API: `dcn42_mmhubbub_set_fgcg(struct dcn30_mmhubbub *mcif_wb30, bool enabled)` writes `MMHUBBUB_CLOCK_CNTL.MMHUBBUB_FGCG_REP_DIS` to `!enabled`.

Control flow: the function is a single register update; there is no constructor or writeback behavior override in this file.

State/persistence: changes persistent hardware clock-control state. It relies on `mcif_wb30` carrying register pointers compatible with `dcn35_mmhubbub_registers`, shift, and mask structs.

Dependencies/integration: includes DCN35 and DCN42 headers plus `reg_helper`. It is used by DCN4.2 resource code when FGC gating must be toggled.

Risks: cast compatibility with DCN35 layout is assumed. The register field is disable-polarity, so incorrect boolean handling reverses the requested behavior.

Test signals: DCN4.2 clock-gating toggles, register readback, and display/writeback stability with FGC on and off.
