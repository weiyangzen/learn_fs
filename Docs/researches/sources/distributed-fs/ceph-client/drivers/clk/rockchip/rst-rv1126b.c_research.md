# sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rv1126b.c

Purpose: RV1126B reset-controller LUT spanning top, bus, peri, core, PMU, PMU1, DDR, SUBDDR, VI, VEPU, NPU, VDO, and VCP CRU islands.

Important APIs/types/functions: island-specific macros such as `TOPCRU_RESET_OFFSET()`, `BUSCRU_RESET_OFFSET()`, `PERICRU_RESET_OFFSET()`, `CORECRU_RESET_OFFSET()`, `PMUCRU_RESET_OFFSET()`, `PMU1CRU_RESET_OFFSET()`, `DDRCRU_RESET_OFFSET()`, `SUBDDRCRU_RESET_OFFSET()`, `VICRU_RESET_OFFSET()`, `VEPUCRU_RESET_OFFSET()`, `NPUCRU_RESET_OFFSET()`, `VDOCRU_RESET_OFFSET()`, and `VCPCRU_RESET_OFFSET()`. `rv1126b_rst_init()` registers `rv1126b_register_offset[]`.

Control flow: called by `rv1126b_clk_init()` after clocks are registered. The common reset controller uses the LUT to convert reset IDs to bank/bit writes under `ROCKCHIP_SOFTRST_HIWORD_MASK`.

State and persistence: static mapping data and hardware reset bits. Assert/deassert state persists in CRU registers until changed.

Dependencies and integration: RV1126B reset dt-bindings, RV1126B CRU offset macros from `clk.h`, common Rockchip `softrst.c`, and reset consumers across CPU, buses, crypto, serial, audio, PMU, DDR, image/video, NPU, and VCP domains.

Risks: the file covers many separately based CRUs by encoding byte offsets into the lookup value; incorrect base arithmetic can send reset writes to the wrong island. PVTPLL-related resets must align with clock source initialization in `clk-rv1126b.c`.

Test signals: reset phandle probes on RV1126B DTs, targeted reset toggles across every CRU island, NPU/VI/VEPU/VDO/VCP subsystem bring-up, and cross-check binding IDs against nonzero intended mappings.
