# sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3562.c

Purpose: RK3562 reset-controller LUT spanning multiple CRU address islands: main CRU, PMU0, PMU1, DDR, SUBDDR, and PERI.

Important APIs/types/functions: `RK3562_CRU_RESET_OFFSET()`, `RK3562_PMU0CRU_RESET_OFFSET()`, `RK3562_PMU1CRU_RESET_OFFSET()`, `RK3562_DDRCRU_RESET_OFFSET()`, `RK3562_SUBDDRCRU_RESET_OFFSET()`, and `RK3562_PERICRU_RESET_OFFSET()` encode island base offsets into one LUT value. `rk3562_rst_init()` registers `rk3562_register_offset[]`.

Control flow: reset consumers call common reset ops; common code looks up the ID, divides by 16 to choose the bank, and writes high-word mask bits. Because this file encodes island offsets as large bank values, one reset controller can cover all CRU islands from a single mapped base.

State and persistence: immutable LUT plus CRU hardware reset bits. No local runtime state.

Dependencies and integration: RK3562 reset bindings, common Rockchip reset controller, RK3562 CRU address layout from `clk.h`, and DT reset phandles for CPU, NPU, GPU, media, display, PHP, bus, PMU, DDR, storage, USB, serial, crypto, and GPIO blocks.

Risks: base offset arithmetic uses byte offsets multiplied by four to match the common reset bank calculation. Any mismatch with mapped CRU aperture layout corrupts target bank selection. Sparse missing IDs may default to zero if binding/table coverage diverges.

Test signals: hardware reset tests across every island, especially PMU and DDR resets; boot with broad peripheral coverage; binding-table consistency checks; and register trace validation that each ID writes the intended `*_SOFTRST_CON` register.
