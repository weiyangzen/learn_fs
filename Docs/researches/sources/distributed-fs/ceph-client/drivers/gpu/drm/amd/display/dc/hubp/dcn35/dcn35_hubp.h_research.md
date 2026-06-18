# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn35/dcn35_hubp.h

Purpose: declares DCN 3.5 HUBP extensions, mainly the additional fine-grain clock gating field and typed shift/mask wrappers that extend the DCN 3.2 register field list.

Important APIs and types: `HUBP_MASK_SH_LIST_DCN35()` composes DCN 3.2 fields and adds `HUBP_FGCG_REP_DIS`. `DCN35_HUBP_REG_FIELD_VARIABLE_LIST(type)` embeds `DCN32_HUBP_REG_FIELD_VARIABLE_LIST(type)` and appends the FGC field. `struct dcn35_hubp2_shift` and `struct dcn35_hubp2_mask` provide generation-specific shift/mask layouts. Prototypes declare construction, FGC control, pixel format programming, surface config, and init.

Control flow: no executable flow exists here. The typed mask/shift structs are used by `dcn35_hubp.c` to safely access the added field before casting to base structures for inherited helpers.

State and persistence: the additional state is the `HUBP_FGCG_REP_DIS` bit in `HUBP_CLK_CNTL`, which controls fine-grain clock-gating repeat disable behavior. Surface state is programmed by declared functions in the implementation.

Dependencies and integration points: includes DCN 3.1 and DCN 3.2 HUBP headers. It is also included by DCN 4.2, which reuses the DCN 3.5 mask base for a different later-generation path.

Risks and test signals: struct layout must remain compatible with inherited DCN 3.2 field lists. If `HUBP_FGCG_REP_DIS` is missing or shifted incorrectly, power management can malfunction without obvious compile-time errors. Signals include generation-specific register table builds, clock-gating tests, DCN 3.5 plane bring-up, and checking that inherited DCN 3.2 fields still map correctly.
