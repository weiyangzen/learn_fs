# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-infracfg.c

## Purpose

This MT6795 infracfg driver provides always-on infrastructure clocks, two CA53 CPU muxes, and an infracfg reset controller. It covers debug, SMI, audio, GCE, L2C SRAM, M4U, MD1, device APC, TRNG, CPUM, keypad, and related bus clocks.

## Important APIs, types, and functions

The central data is `infra_gates[]`, `cpu_muxes[]`, `infra_ao_rst_ofs[]`, `infra_ao_idx_map[]`, and `clk_rst_desc`. `clk_mt6795_infracfg_probe()` maps the resource, allocates `CLK_INFRA_NR_CLK`, registers resets with `mtk_register_reset_controller_with_dev()`, gates with `mtk_clk_register_gates()`, CPU muxes with `mtk_clk_register_cpumuxes()`, and publishes the onecell provider. Remove unregisters the provider, CPU muxes, gates, and allocation.

## Control flow, state, and persistence

The probe is linear with unwind labels for composite/gate failures. Gate registers use set/clear/status offsets `0x40`, `0x44`, and `0x48` with `mtk_clk_gate_ops_no_setclr`, while CPU muxes live at offset `0x00` and select between `clk26m`, `armca53pll`, `mainpll`, and `univpll`. The reset controller exposes selected reset bits from banks at `0x30` and `0x34`. State is CCF/reset registration plus hardware gate, mux, and reset register state.

## Dependencies and integration points

Dependencies include `clk-cpumux.h`, `clk-gate.h`, `clk-mtk.h`, `reset.h`, `dt-bindings/clock/mediatek,mt6795-clk.h`, and `dt-bindings/reset/mediatek,mt6795-resets.h`. The provider is bound by `"mediatek,mt6795-infracfg"` and consumed by core bus, modem, security, keypad, and multimedia subsystems.

## Risks and test signals

Risks include reset index-map mistakes, CPU mux parent mistakes, and gate polarity/register offset mismatch. Test by validating CPU frequency switching, reset lines for scpsys/PMIC wrap/MIPI/MM IOMMU, and clock summary entries for all `infra_*` clocks after boot.
