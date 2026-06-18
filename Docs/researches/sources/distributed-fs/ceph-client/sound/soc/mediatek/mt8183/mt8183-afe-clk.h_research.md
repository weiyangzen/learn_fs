# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-clk.h

Purpose: declares the MT8183 AFE clock-control API shared by the AFE core and DAI implementations.

Important APIs/types/functions: defines APLL widget names `APLL1_W_NAME` and `APLL2_W_NAME`, enum IDs `MT8183_APLL1`/`MT8183_APLL2`, forward-declares `struct mtk_base_afe`, and declares init, AFE clock enable/disable, APLL enable/disable, APLL selection helpers, and MCK enable/disable functions.

Control flow: included by `mt8183-afe-clk.c` for definitions and by I2S/TDM/AFE code for calls. DAPM event handlers use these declarations to toggle APLL and MCLK resources; runtime PM uses the AFE clock functions.

State and persistence: no storage in the header; state is carried through `struct mtk_base_afe` and its MT8183 private data.

Dependencies and integration: depends on the MediaTek common AFE object type but avoids including the full definition. The APLL widget names must match DAPM routes in I2S/TDM files.

Risks: no bounds or type safety around integer APLL/MCK IDs; callers must use IDs from `mt8183-afe-common.h`. Changing widget-name strings would break DAPM route predicates.

Test signals: compile all MT8183 objects together, modpost export checks, and runtime DAPM paths that exercise every declared function.
