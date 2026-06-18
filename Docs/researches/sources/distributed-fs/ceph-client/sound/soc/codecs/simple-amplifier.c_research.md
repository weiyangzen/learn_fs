# sources/distributed-fs/ceph-client/sound/soc/codecs/simple-amplifier.c

Purpose: generic platform ASoC component for simple analog amplifiers. It exposes stereo inputs/outputs, an optional enable GPIO, and a DAPM-managed `VCC` regulator supply without any DAI or register map.

Important APIs and data: `struct simple_amp` stores only the optional enable GPIO. DAPM widgets are `INL`, `INR`, `DRV`, `OUTL`, `OUTR`, and `SND_SOC_DAPM_REGULATOR_SUPPLY("VCC", 20, 0)`. `drv_event()` asserts the enable GPIO on POST_PMU and deasserts it on PRE_PMD.

Control flow: platform probe allocates private data, requests optional `enable` GPIO low, stores driver data, and registers an ASoC component with no DAIs. DAPM routes connect both inputs through `DRV`, require `VCC` for each output, and connect driver output to both outputs.

State and persistence: state is only the GPIO level and DAPM regulator state. No cache, clock, PM runtime, or format handling exists.

Dependencies and integration points: platform/OF binding supports `dioo,dio2125` and `simple-audio-amplifier`. It integrates with machine-card DAPM graphs as a passive component between CPU/codec outputs and speakers. Risks include no enable delay, no regulator voltage constraints, no mono route specialization, and WARN on unexpected DAPM events. Test signals are DAPM path activation, GPIO transition timing, regulator enable/disable, optional GPIO absence, and integration in board audio routes.
