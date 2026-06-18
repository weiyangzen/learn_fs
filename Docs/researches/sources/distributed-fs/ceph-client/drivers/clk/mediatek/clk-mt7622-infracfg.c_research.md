# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-infracfg.c

## Purpose

This MT7622 infracfg driver registers core infrastructure gates, one CPU mux, and a simple reset controller. It supplies clocks for debug, TRNG, audio, IRRX, APXGPT, and PMIC paths.

## Important APIs, types, and functions

Important definitions are `infra_cg_regs`, `infra_mux1_parents`, `cpu_muxes[]`, `infra_clks[]`, `infrasys_rst_ofs[]`, and `clk_rst_desc`. `clk_mt7622_infracfg_probe()` performs explicit reset, gate, CPU-mux, and provider registration with unwind labels; remove unregisters provider, CPU muxes, gates, and data.

## Control flow, state, and persistence

Probe maps the resource, allocates `CLK_INFRA_NR_CLK`, registers reset bank `0x30`, registers set/clear gates at offsets `0x40/0x44/0x48`, registers `infra_mux1_sel` at offset `0x0`, and publishes the OF provider. State is hardware gate/mux/reset bits and CCF/reset objects.

## Dependencies and integration points

Dependencies include `clk-cpumux.h`, `clk-gate.h`, `clk-mtk.h`, `reset.h`, and MT7622 bindings. Parent clocks include `clkxtal`, `armpll`, `main_core_en`, `axi_sel`, `aud_intbus_sel`, `irrx_sel`, `f10m_ref_sel`, and `pmicspi_sel`. It integrates with CPU clocking, PMIC, timers, audio, and reset consumers.

## Risks and test signals

Risks include CPU mux parent ordering, reset-controller registration failure, and missing gate unwind. Test CPU mux switching, TRNG/timer/PMIC/audio consumers, and reset lines.
