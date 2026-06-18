# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-ddr.c

## Purpose
Registers Rockchip DDR clocks whose rate control is delegated to firmware through ARM SMCCC SIP calls. The CCF clock exposes set, recalc, determine-rate, and get-parent operations while firmware owns DRAM frequency programming.

## Important APIs, Types, and Functions
`struct rockchip_ddrclk` stores CCF hardware, CRU base, mux/divider field positions, DDR type, and lock. `rockchip_ddrclk_sip_set_rate()` calls `ROCKCHIP_SIP_DRAM_FREQ` with `SET_RATE`. `rockchip_ddrclk_sip_recalc_rate()` asks firmware for current rate. `rockchip_ddrclk_sip_determine_rate()` asks firmware to round the requested rate. `rockchip_clk_register_ddrclk()` selects SIP ops for `ROCKCHIP_DDRCLK_SIP`.

## Control Flow, State, and Persistence
Persistent state is the allocated DDR clock. Rate changes are serialized by the supplied lock around the SMC call. Parent selection is read from the mux register, while rate state is firmware-owned.

## Dependencies, Integration Points, Risks, and Test Signals
The helper depends on ARM SMCCC, Rockchip SIP firmware IDs, CCF, MMIO, and SoC mux/divider descriptors. It exports `rockchip_clk_register_ddrclk()`. Risks are missing firmware, SIP ABI mismatch, SMC errors, and stale local mux information. Test firmware round-rate, DRAM frequency transitions under stress, get-parent accuracy, and unsupported flag rejection.
