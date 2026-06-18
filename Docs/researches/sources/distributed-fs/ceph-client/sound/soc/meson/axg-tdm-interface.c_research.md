# sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm-interface.c

Purpose: Implements the AXG TDM interface DAI, which owns pad/loopback stream objects, validates TDM slot masks and widths, configures master/sample/bit clocks, enforces rate constraints and component-wide symmetry, and starts/stops attached formatters through the TDM stream API.

Important APIs and functions: Exported `axg_tdm_set_tdm_slots()` records per-lane TX/RX masks, slot count, slot width, channel maxima, and format masks. DAI ops include `set_sysclk`, `set_fmt`, `startup`, `hw_params`, `hw_free`, `trigger`, probe, and remove. Helpers include `axg_tdm_slots_total()`, `axg_tdm_iface_set_stream()`, `axg_tdm_iface_set_sclk()`, and `axg_tdm_iface_set_lrclk()`.

Control flow: DAI probe allocates an `axg_tdm_stream` for each stream direction with a widget. Card init calls `axg_tdm_set_tdm_slots()` before runtime to install masks and narrow channel/format capabilities. Startup rejects streams with no slots, applies an existing active component rate as a hard constraint or computes max rate from `MAX_SCLK / (slots * slot_width)`. `hw_params` validates the DAI format, checks channel count versus slots and sample width versus slot width, stores stream parameters, programs sclk/lrclk when CPU is clock master, and applies continuous clocks if requested. Trigger starts/stops the corresponding stream, which in turn enables/disables attached formatters. Bias level manages mclk when entering/leaving PREPARE.

State and persistence: `struct axg_tdm_iface` stores clocks, mclk rate, common format, slot geometry, and active rate. `axg_tdm_stream` objects are attached to playback/capture DMA data. DAI driver instances are duplicated at probe because slot masks mutate per-instance channel maxima and formats.

Dependencies and integration points: Called by `axg-card.c` during TDM backend initialization and by formatter code at stream start/stop. Uses common clock rate/phase/duty-cycle APIs, ASoC DAI and DAPM APIs, and `axg-tdm.h` inversion helpers.

Risks: CPU-master mode requires mclk; slave mode can omit it. MCLK must divide exactly into the desired bit clock if a fixed mclk rate was requested. I2S/left/right-justified formats reject slot counts above two, while DSP modes allow larger TDM frames. The error message says "has not slots" but the functional risk is missing mask configuration. Trigger ignores return from `axg_tdm_stream_start()`, so formatter-start failures may not propagate.

Test signals: TDM pad playback/capture, loopback capture, CPU master and slave clocking, `mclk-fs` sysclk requests, I2S versus DSP_A/B formats, continuous-clock links, invalid masks/slot widths, and multi-stream rate symmetry.
