# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-apmixedsys.c

## Purpose
`clk-mt8195-apmixedsys.c` registers MT8195 AP mixed-signal PLL clocks and AP mixed gates. It supplies root PLLs and frequency-hopping-capable clock hardware to the rest of the MT8195 tree.

## Important APIs, Types, And Functions
The file defines AP mixed gate registers, `apmixed_clks`, `plls`, and `pllfhs`. `clk_mt8195_apmixed_probe()` allocates `CLK_APMIXED_NR_CLK` storage, calls `fhctl_parse_dt()` for `mediatek,mt8195-fhctl`, registers PLLFH clocks and gates, and publishes an OF provider for `mediatek,mt8195-apmixedsys`.

## Control Flow, State, And Persistence
Probe parses FHCTL metadata before registering PLLFH clocks, then registers gates and the provider. Error handling and remove unwind gates, PLLFH registrations, and clock data in reverse order. State consists of PLL hardware registrations, frequency hopping metadata, gates, and OF provider data.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `clk-pllfh`, FHCTL DT, MT8195 clock IDs, and topckgen consumers. Risks include root PLL rate errors, FHCTL mismatch, and provider publication failures leaving downstream clocks unavailable. Test signals include topckgen parent rates, PLL rate changes, FHCTL-enabled boot, clock summary checks, and remove/reprobe cleanup.
