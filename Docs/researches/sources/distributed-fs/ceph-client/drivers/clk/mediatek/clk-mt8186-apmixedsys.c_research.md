<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-apmixedsys.c

Purpose: This driver registers MT8186 apmixedsys PLLs using PLLFH/FHCTL support for CPU, CCI, main, universal, storage, MM, NNA, ADSP, MFG, TVD, and audio PLLs.

Important APIs, types, and functions: `plls` defines `struct mtk_pll_data` with MT8186 min/max and integer-bit settings. `pllfhs` maps PLL IDs to FHCTL data. `clk_mt8186_apmixed_probe` maps MMIO, allocates `CLK_APMIXED_NR_CLK`, parses optional `mediatek,mt8186-fhctl`, registers PLLFH clocks with `mtk_clk_register_pllfhs`, and publishes an OF provider. Remove unregisters provider and PLLFH clocks.

Control flow: The platform driver binds `mediatek,mt8186-apmixedsys`; probe prepares all root PLLs before topckgen and subsystem consumers rely on them. Error paths unregister PLLFH state if provider publication fails.

State and persistence behavior: PLL and FH state is hardware register state; provider data is volatile. No persistent storage is used.

Dependencies and integration points: It depends on `clk-fhctl.h`, `clk-pllfh.h`, `clk-pll.h`, MT8186 bindings, optional FHCTL DT, and root consumers in topckgen, CPU, AI, ADSP, display, storage, video, and audio domains.

Risks and edge cases: FHCTL tables must align with PLL hardware IDs and offsets. Missing or malformed FHCTL node should not prevent basic PLL registration. Root clock errors cascade into many subsystem probe failures.

Test signals: Boot with FHCTL present/absent, validate PLL rates and frequency hopping registration, CPU/AI/ADSP/display/storage workloads, error-path cleanup, and remove/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-apmixedsys.c -->
