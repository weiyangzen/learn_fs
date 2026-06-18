# sources/distributed-fs/ceph-client/sound/soc/ti/davinci-mcasp.c

## Purpose
Main TI McASP CPU DAI driver for DaVinci/Sitara/OMAP/DRA/K3 systems. It supports multichannel IIS/TDM and DIT S/PDIF, EDMA/SDMA/UDMA PCM backends, optional GPIO mode, xrun IRQs, clock/divider programming, constraints, and runtime PM context restore.

## Important APIs/types/functions
Core state is `struct davinci_mcasp`; PM uses `struct davinci_mcasp_context`; constraints use `struct davinci_mcasp_ruledata`. DAI callbacks include set_fmt, set_clkdiv, set_sysclk, set_tdm_slot, startup/shutdown, hw_params, trigger, delay, and DAI probe. Helpers parse config, choose DMA type, calculate DMA offsets, register GPIO, and handle IRQs.

## Control flow
Probe maps registers, enables runtime PM, parses op mode, TDM slots, async mode, serializers, FIFO depths, aux ratios, and dismod, requests IRQs, prepares DMA addresses, allocates channel constraints, detects DMA controller, registers the PCM provider and DAI, then optionally registers GPIO. DAI setup programs frame/clock roles, inversion, sysclk, dividers, masks, serializers, FIFO thresholds, format rotation, IEC958 status, and constraints. Trigger sequences clocks, serializers, FIFO enable, IRQ masks, and pin directions.

## State, dependencies, integration, risks, tests
State includes DMA data, pdata, MMIO base, substreams, DAI format, IEC958 status, TDM settings, serializers, clocks, async mode, pdir, FIFO depths, data-port mode, constraints, IRQ masks, GPIO chip, and PM context. Dependencies are ASoC, ALSA constraints, TI DMA PCM providers, clocks, PM runtime, OF/property, GPIO, platform data, and register definitions. Risks include async/sync clock interactions, serializer/channel mismatch, FIFO divisibility, divider accuracy, DIT TX-only behavior, DMA detection side effects, GPIO/audio pin conflicts, and PM omissions. Test IIS full-duplex, async slots, DIT rates/controls, EDMA/SDMA/UDMA, xrun IRQs, GPIO-only mode, and suspend/resume.
