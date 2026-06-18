# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-clk.c

## Purpose

This file handles MT6797 AFE clock lookup and global clock enable/disable sequencing.

## Important APIs, Types, and Functions

- Internal clock IDs cover infra audio, infra 26 MHz, top audio mux, audio bus mux, two PLL parents, and 26 MHz parent.
- `mt6797_init_clock()` allocates `afe_priv->clk` and obtains all named clocks.
- `mt6797_afe_enable_clock()` enables infra clocks and top muxes, sets `top_mux_audio` parent to 26 MHz, and enables the audio bus mux.
- `mt6797_afe_disable_clock()` disables bus, mux, 26 MHz, and infra clocks.

## Control Flow

Probe initializes handles. Runtime resume enables clocks in dependency order; runtime suspend disables them. Error labels unwind earlier enables when later steps fail.

## State and Persistence Behavior

Clock pointers persist in `mt6797_afe_private`. Hardware clock state changes only during runtime PM or explicit callers.

## Dependencies and Integration Points

Uses Common Clock Framework and is called from `mt6797-afe-pcm.c` runtime PM and probe.

## Risks and Edge Cases

The enable error path logs failures but returns `0` after unwinding instead of the failing `ret`, which can make runtime resume/probe appear successful with clocks disabled. Parent selection is fixed to 26 MHz, so boards requiring a different parent are unsupported here.

## Test Signals

Clock failure injection should verify returned errors. Runtime PM traces should show balanced enable/disable counts. Boot logs should confirm all DT clock names are found.
