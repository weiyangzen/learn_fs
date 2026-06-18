# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-clk.h

## Purpose
This header defines the MT8195 AFE clock ID namespace and declares the clock-control functions implemented by `mt8195-afe-clk.c`. It is the common interface used by MT8195 PCM, DAI, and machine-driver code to acquire, enable, disable, prepare, parent, and rate-control AFE-related clocks.

## Important APIs, Types, and Definitions
The first enum defines `MT8195_CLK_*` IDs for the 26 MHz crystal, APLL roots, APLL dividers, top muxes, infrastructure/audio clock gates, ADSP audio DSP clock, AFE master clock, APLL tuners, DAC/ADC/hires clocks, I2S/TDM/HDMI/ASRC clocks, A1SYS/A2SYS/PCMIF clocks, and individual memif gates. The second enum defines MCLK source selectors such as `MT8195_MCK_SEL_26M`, `MT8195_MCK_SEL_APLL1`, and `MT8195_MCK_SEL_APLL2`, with placeholders for APLL3-5 and HDMI RX APLL. The third enum defines tuner IDs `MT8195_AUD_PLL1` through `MT8195_AUD_PLL5`.

Function declarations cover MCLK source mapping/rate/default choice, clock initialization, generic enable/disable/prepare/unprepare helpers, atomic enable/disable helpers, clock rate and parent updates, main clock sequencing, and register-read/write clock sequencing.

## Control Flow
There is no implementation control flow in the header. It constrains caller control flow by separating initialization (`mt8195_afe_init_clock()`), generic one-clock operations, atomic vs sleepable clock operations, register-access clock gates, and main AFE clock bring-up/tear-down.

## State and Persistence
The header itself holds no state. Its enum values index `mt8195_afe_private->clk`, so ordering is state-significant: any mismatch between enum order and the implementation clock-name table would route callers to the wrong clock. MCLK and tuner IDs are also persisted indirectly in DAI private data and runtime configuration code.

## Dependencies and Integration Points
It forward-declares `struct mtk_base_afe` and uses `struct clk` pointers in prototypes. It integrates with MT8195 AFE implementation files, DAI drivers, machine drivers, and Linux CCF. It must stay synchronized with `mt8195-afe-clk.c` and with device-tree clock bindings/names.

## Risks
Adding, removing, or reordering enum values without updating `aud_clks[]` and all clock users can silently misconfigure hardware. The MCLK selector enum advertises APLL3-5/HDMIRX choices, but the current implementation only maps 26M/APLL1/APLL2; callers using unsupported selectors receive errors or zero rates. Atomic helpers require callers to prepare clocks elsewhere.

## Test Signals
Compile tests should catch missing declarations and enum names. Runtime signals include correct clock lookup for every enum index, successful DAI paths that rely on memif/ETDM/ADDA clock IDs, expected MCLK parent/rate selection for 8 kHz-family and 44.1 kHz-family rates, and no CCF warnings about unprepared atomic clock enables.
