# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_utils.c

## Purpose
`fsl_utils.c` provides shared Freescale/NXP ASoC helpers for legacy DMA phandle resolution, PLL clock discovery/reparenting, clock-derived PCM rate constraints, and runtime-PM-safe wrappers around volatile ALSA mixer controls.

## Important APIs, Types, And Functions
Exported functions are `fsl_asoc_get_dma_channel`, `fsl_asoc_get_pll_clocks`, `fsl_asoc_reparent_pll_clocks`, `fsl_asoc_constrain_rates`, `fsl_asoc_get_xr_sx`, `fsl_asoc_put_xr_sx`, `fsl_asoc_get_enum_double`, `fsl_asoc_put_enum_double`, `fsl_asoc_get_volsw`, and `fsl_asoc_put_volsw`.

## Control Flow
`fsl_asoc_get_dma_channel` parses a named phandle from an SSI node, validates `fsl,ssi-dma-channel`, derives the platform name from the DMA channel resource address and node name, and returns DMA channel/controller IDs from `cell-index`. `fsl_asoc_get_pll_clocks` optionally acquires `pll8k` and `pll11k`. `fsl_asoc_reparent_pll_clocks` walks parent clocks until it finds either PLL and reparents to the 8 kHz or 11.025 kHz family based on divisibility of the requested ratio by 8000. `fsl_asoc_constrain_rates` filters an original rate list to rates that divide at least one available PLL/external clock, falling back to the original list if no match is found.

The mixer wrappers resume the component device with `pm_runtime_resume_and_get`, call the standard ASoC get/put implementation, suppress positive change notifications for volatile put operations by returning zero, and drop runtime PM with autosuspend.

## State And Persistence
The file does not own long-lived state. It writes caller-provided DMA IDs/platform name buffers, returns clock pointers acquired through devm, mutates caller-provided rate constraint/list storage, and temporarily changes device runtime PM state around volatile control access.

## Dependencies And Integration Points
It depends on Linux clocks, clock provider parent inspection, OF address parsing, runtime PM, and ASoC mixer helpers. SAI and XCVR use PLL helpers and rate constraints; SAI and XCVR timestamp controls use the runtime-PM-safe mixer wrappers; legacy PowerPC/i.MX machine code can use DMA channel lookup.

## Risks And Edge Cases
`fsl_asoc_get_dma_channel` relies on legacy `cell-index` properties and manually builds a platform name to match ASoC platform devices. `fsl_asoc_reparent_pll_clocks` mutates the local `ratio` with `do_div`, so callers should pass a value, not expect it preserved. Rate constraints depend on current clock rates, and null clocks are treated as rate zero. Mixer wrappers return immediately on runtime PM failure, which surfaces PM issues to userspace controls.

## Test Signals
Validate legacy SSI DMA lookup on old DT bindings, check rate constraints with only 8 kHz PLL, only 11.025 kHz PLL, both PLLs, and no PLLs, verify parent switch when changing between 48 kHz-family and 44.1 kHz-family rates, and read/write timestamp or other volatile kcontrols while the device is runtime suspended.
