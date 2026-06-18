<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/j721e-evm.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/j721e-evm.c

## Purpose
ASoC machine driver for TI J721E/J7200 common processor board audio, optionally with the IVI extension. It describes PCM3168A codec links, McASP CPU DAIs, DAPM board endpoints, and clock-parent/rate policy for the CPB and IVI audio domains.

## APIs, Types, and Functions
Key state is `struct j721e_priv`, which owns the card, dynamic DAI links, codec prefixes, rate interval, PLL/HSDIV rates, two `struct j721e_audio_domain` instances, and a mutex. Important helpers are `j721e_configure_refclk()`, `j721e_audio_startup()`, `j721e_audio_hw_params()`, `j721e_audio_shutdown()`, `j721e_audio_init()`, `j721e_audio_init_ivi()`, `j721e_get_clocks()`, `j721e_calculate_rate_range()`, `j721e_soc_probe_cpb()`, `j721e_soc_probe_ivi()`, and `j721e_soc_probe()`. OF compatibles select CPB, CPB+IVI, or J7200 clock data.

## Control Flow, State, and Persistence
Probe parses the card model, phandles for McASP and PCM3168A codec nodes, named codec/McASP clocks, and creates playback/capture DAI links. Startup serializes domain use, enforces a shared active sample rate across domains when any stream is active, and resets CPU/codec TDM slots to stereo 32-bit. `hw_params` chooses 16- or 32-bit slots, selects a 48 kHz or 44.1 kHz PLL family, reparents codec and McASP clocks, sets SCKI to 256/512/768 x sample rate, and records the domain rate. Shutdown clears the domain rate when the active count reaches zero.

## Dependencies and Integration
Depends on ASoC machine-card APIs, OF phandles/properties, common clock framework, PCM3168A codec DAI names, and TI McASP `MCASP_CLK_HCLK_AUXCLK`. It integrates with device tree bindings using `model`, `ti,cpb-mcasp`, `ti,cpb-codec`, `ti,ivi-mcasp`, `ti,ivi-codec-a`, and `ti,ivi-codec-b`.

## Risks and Test Signals
Risks include shared-rate constraints blocking mixed-rate domain usage, missing optional 44.1 kHz parents on J7200 limiting rate families, stale `hsdiv_rates` when two domains share parent IDs, OF node reference lifetime leaks on success paths, and `-ENOTSUPP` masking if a codec cannot accept TDM/sysclk setup. Test signals are probe for all compatibles, CPB-only and IVI route creation, 44.1/48 kHz family playback and capture, simultaneous CPB/IVI stream constraints, 16-bit versus wider slot width, and failure paths for absent clocks/phandles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/j721e-evm.c -->
