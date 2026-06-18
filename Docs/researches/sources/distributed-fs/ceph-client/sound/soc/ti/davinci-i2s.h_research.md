# sources/distributed-fs/ceph-client/sound/soc/ti/davinci-i2s.h

## Purpose
Small ABI header for the DaVinci ASP/I2S DAI clock divider.

## Important APIs/types/functions
Defines `enum davinci_mcbsp_div` with `DAVINCI_MCBSP_CLKGDV`, the sample-rate generator divider ID.

## Control flow
No executable code. Machine drivers pass the enum through `snd_soc_dai_set_clkdiv`; `davinci_i2s_dai_set_clkdiv` stores the value.

## State, dependencies, integration, risks, tests
No state is defined; divider state lives in `struct davinci_mcbsp_dev`. It integrates machine drivers with `davinci-i2s.c`. Risks are enum drift or unsupported IDs. Build users and validate generated clocks at runtime.
