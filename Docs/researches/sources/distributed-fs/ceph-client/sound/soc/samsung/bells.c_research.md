# sources/distributed-fs/ceph-client/sound/soc/samsung/bells.c

## Purpose
Machine driver for Wolfson Bells boards with WM2200, WM5102, or WM5110 codec topologies. It wires AP-to-DSP, DSP-to-codec, optional baseband, and optional sub-speaker links, and manages Arizona/WM0010/WM9081 clocks.

## Important APIs, Types, And Functions
- `struct bells_drvdata` holds per-card SYSCLK and ASYNCCLK rates.
- `bells_set_bias_level()` starts FLL1 and optional FLL2 when entering prepare from standby.
- `bells_set_bias_level_post()` stops FLLs when returning to standby.
- `bells_late_probe()` configures codec SYSCLK/ASYNCCLK/OPCLK, WM0010 clock, AIF clocks, and WM9081 MCLK depending on available runtime links.
- Static DAI link arrays model WM2200, WM5102, and WM5110 variants.

## Control Flow
Platform ID selects one of three static cards. Registration is simple; late probe then locates relevant runtimes by link index and programs clock trees. Bias-level transitions dynamically start and stop codec FLLs around DAPM power changes.

## State And Persistence
Per-card clock rates are static `drvdata`. Runtime FLL/sysclk state persists in the attached codec components until bias transitions change it. No private allocation or disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S, WM0010 DSP component, WM2200/WM5102/WM5110 codecs, WM1250 EV1, WM9081, DAPM, and platform device IDs. Codec-conf prefixes distinguish the sub WM9081.

## Risks And Edge Cases
- Uses static cards indexed by `pdev->id`; invalid IDs would index out of bounds because probe does not validate.
- Late probe uses numeric DAI indexes and `card->num_rtd` comparisons, so topology changes are fragile.
- FLL startup errors are logged in bias prepare but some paths continue returning success.

## Test Signals
Platform-device probe for ids 0-2, link creation count, DAPM bias transitions with FLL start/stop traces, late-probe clock programming, and baseband/sub link audio smoke tests.
