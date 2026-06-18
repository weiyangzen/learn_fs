# sources/distributed-fs/ceph-client/sound/soc/ti/davinci-i2s.c

## Purpose
DaVinci ASP/McBSP-compatible I2S CPU DAI driver. It drives the older DaVinci Audio Serial Port block and connects it to EDMA PCM.

## Important APIs/types/functions
Private state is `struct davinci_mcbsp_dev`. DAI callbacks include `davinci_i2s_set_dai_fmt`, `davinci_i2s_dai_set_clkdiv`, `davinci_i2s_set_tdm_slot`, `davinci_i2s_hw_params`, `davinci_i2s_prepare`, `davinci_i2s_trigger`, `davinci_i2s_shutdown`, and `davinci_i2s_dai_probe`. Probe/remove manage resources.

## Control flow
Probe maps registers, reads T1 framing flags, fills TX/RX DMA addresses/filter data, gets functional/external clocks, registers the component, and registers EDMA PCM. Format setup programs PCR/SPCR/SRGR for clock roles, DSP/I2S emulation, inversion, free-running mode, and TDM restrictions. `hw_params` computes word length, sample-rate generator values, control fields, and optional channel-combine behavior. Prepare/trigger reset and start/stop TX/RX.

## State, dependencies, integration, risks, tests
State includes MMIO base, DMA data/request IDs, PCR/mode/fmt/divider/TDM settings, clocks, and T1 flags. Dependencies are ASoC, EDMA PCM, clocks, DT/resources, and DaVinci machine drivers. Risks include pseudo-I2S limitations, TDM all-slot masks, divider rounding, no PM regcache, and channel-combine swaps. Test formats, clock-provider modes, TDM, suspend, and DMA paths.
