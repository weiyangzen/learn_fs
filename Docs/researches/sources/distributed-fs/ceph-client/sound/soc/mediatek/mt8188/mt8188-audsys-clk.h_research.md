# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-audsys-clk.h

Purpose: Small public header for the local audsys gate-clock registration helper.

Important API: Declares `int mt8188_audsys_clk_register(struct mtk_base_afe *afe);`, implemented in `mt8188-audsys-clk.c` and called from `mt8188_afe_init_clock()` before the driver resolves its clock array.

Control flow and integration: This header is included by `mt8188-afe-clk.c`, making audsys gate registration part of the higher-level AFE clock initialization sequence. The registration helper installs clock provider objects and clkdev lookups scoped to the AFE device.

State and persistence: The header has no state. The function it declares populates `mt8188_afe_private->lookup` and registers common-clock-framework gate objects.

Dependencies: The prototype references `struct mtk_base_afe` without a local forward declaration. Current include order works because callers include common AFE headers first; future direct users should include the common header or add a forward declaration.

Risks: Because this header exposes only a single helper and no type definitions, drift risk is low. The main maintenance risk is include hygiene: direct inclusion without a prior declaration of `struct mtk_base_afe` can produce compiler warnings or errors depending on context.

Test signals: Compile coverage of `mt8188-afe-clk.c` is sufficient for this header. Probe success through `mt8188_afe_init_clock()` confirms the declared integration path is functioning.
