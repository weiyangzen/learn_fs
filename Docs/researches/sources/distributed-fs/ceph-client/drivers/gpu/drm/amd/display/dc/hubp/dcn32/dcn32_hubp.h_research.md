# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn32/dcn32_hubp.h

Purpose: declares DCN 3.2 HUBP additions over DCN 3.1, focused on MALL, virtual memory page buffer configuration, SubVP buffering, and UCLK pstate forcing.

Important APIs and definitions: `HUBP_MASK_SH_LIST_DCN32()` composes `HUBP_MASK_SH_LIST_DCN31()` and adds `USE_MALL_SEL`, `USE_MALL_FOR_CURSOR`, `VMPG_SIZE`, `PTE_BUFFER_MODE`, `BIGK_FRAGMENT_SIZE`, `FORCE_ONE_ROW_FOR_FRAME`, and data/cursor `UCLK_PSTATE_FORCE` fields. Public declarations cover pstate forcing, MALL select, SubVP preparation, phantom post-enable, cursor attributes, init, and construction.

Control flow: this is a declaration-only file. The function prototypes become optional `hubp_funcs` entries in `dcn32_hubp.c` and are reused by DCN 4.0.1/4.2 where compatible.

State and persistence: the listed fields program persistent hardware controls for memory-cache residency, cursor cache use, virtual memory request buffering, and pstate transition suppression. They directly affect display fetch behavior during power and memory-clock changes.

Dependencies and integration points: includes DCN 2.0, 2.1, 3.0, and 3.1 HUBP headers. Later HUBP generations include or call these helpers for MALL and SubVP support. The declarations connect to DML and HWSS decisions about static-screen caching, SubVP, and memory-clock transitions.

Risks and test signals: mask list mistakes affect multiple generations because later code reuses these helpers. Pstate and MALL fields are power/performance critical and can create intermittent underflows. Signals include register table builds, DCN 3.2 and later boot, SubVP/MALL validation, cursor cache behavior, and memory-clock transition stress.
