# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-s700.c

Purpose: this file is the Actions S700 CMU provider and reset controller for `actions,s700-cmu`.

Important structures: the file declares CMU offsets, audio/CVBS PLL tables, core/dev/DDR/NAND/display/CVBS/audio/Ethernet PLLs, parent arrays, divider/factor tables, standalone mux/divider/gate clocks, many composite clocks, `s700_clks[]`, `s700_hw_clks`, and `s700_resets[]`. S700 adds CPU/NOC/HP bus muxing, USB2/USB3 gates, LCD/GPU/thermal sensor clocks, PCM1 fixed-factor clock, and I3C-like `irc_switch` gate relative to S500.

Control flow/state: `s700_clk_probe()` follows the same pattern as S500: initialize regmap, allocate an `owl_reset`, register reset ops, and register the onecell clock provider. A FIXME notes reset controller registration should move to common code once all OWL SoCs support it.

Dependencies/integration: depends on `dt-bindings/clock/actions,s700-cmu.h` and `dt-bindings/reset/actions,s700-reset.h`. Uses common OWL helpers for every register-level operation.

Risks and tests: return from regmap initialization is ignored. There are minor spelling/format anomalies such as `CLK_SENOR_SRC` and `clk_cvbs_pll .common`, so binding names and compiler coverage matter. Test signals include S700 boot, CPU/NOC rate reporting, USB/Ethernet/LCD/GPU devices, reset operations, and unused-clock handling.
