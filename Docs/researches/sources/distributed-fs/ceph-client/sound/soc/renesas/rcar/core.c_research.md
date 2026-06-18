# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/core.c

## Purpose

`core.c` is the central ASoC platform driver for Renesas R-Car SRU/SCU/SSIU/SSI audio. It binds generation-compatible devices, owns `rsnd_priv`, builds per-DAI playback/capture module chains from DT, implements the ASoC DAI/component callbacks, sequences module lifecycle callbacks, handles PCM constraints and DPCM conversion metadata, and registers/removes the platform driver.

## Important APIs, types, and functions

The file implements core module helpers (`rsnd_mod_init()`, `rsnd_mod_quit()`, `rsnd_mod_name()`, `rsnd_mod_next()`, `rsnd_dai_connect()`), runtime channel/rate/alignment helpers (`rsnd_runtime_channel_*()`, `rsnd_get_adinr_bit()`, `rsnd_get_dalign()`, `rsnd_get_busif_shift()`), DT parsing helpers (`rsnd_parse_connect_common()`, `rsnd_node_count()`, `rsnd_node_fixed_index()`), ASoC DAI ops (`startup`, `shutdown`, `trigger`, `prepare`, `set_fmt`, `set_tdm_slot`, `pcm_new`), component ops (`hw_params`, `hw_free`, `pointer`), and ALSA mixer-control helpers (`rsnd_kctrl_new()` plus `rsnd_kctrl_init_m/s()`). `rsnd_probe()` runs all module probe functions, performs fallback probing, registers components, and enables runtime PM.

## Control Flow

Probe allocates `rsnd_priv`, sets generation flags from OF match data, initializes gen/dma/ssi/ssiu/src/ctu/mix/dvc/cmd/adg/dai subsystems, then calls `rsnd_rdai_continuance_probe()` for each playback/capture stream. If a module probe returns `-EAGAIN`, the stream is disconnected back to SSI-only and reprobed in PIO fallback mode. Runtime `hw_params` clears conversion fields, reads DPCM BE params when dynamic, records converted rate/channel, bounds SRC ratios, then calls module `hw_params`. Trigger start calls module `init`, `start`, and `irq(enable)` under the spinlock; trigger stop disables IRQ, stops, and quits modules. `rsnd_dai_call()` uses per-direction module order arrays and per-module status nibbles to avoid duplicate init/start/hw_params and to call teardown only when matching setup happened.

## State and Persistence Behavior

`rsnd_priv` persists device-level module arrays, DAI driver arrays, generation flags, component split counts, and the spinlock. Each `rsnd_dai_stream` stores its module slots, DMA module, active substream pointer, converted rate/channel, parent SSI status, flags for HDMI/TDM/hw-rule warnings, and optional DMAC device for PCM buffer allocation. Each `rsnd_mod` stores ID, type, ops, clock, private pointer, and lifecycle status. ALSA control values persist in module-owned `rsnd_kctrl_cfg_*` structures and are applied during module init or control updates.

## Dependencies and Integration Points

The file integrates Linux ASoC, ALSA PCM constraints, OF graph/simple-card parsing, PM runtime, and all R-Car submodules. It depends on `gen.c` for register access through submodule callbacks, on ADG/SSI for clock constraints, and on DMA for PCM buffer device selection. It exposes helpers used by all sibling files via `rsnd.h`.

## Risks and Test Signals

Risks cluster around lifecycle ordering, status-nibble imbalance, DPCM conversion bounds, DT route parsing, TDM split detection, pin-sharing symmetric-rate handling, and fallback from DMA to PIO. Test signals include boot/probe on Gen1/2/3/4 DTs, simple-card and audio-graph bindings, start/stop/resume loops, DPCM SRC conversion, multi-SSI and TDM slot settings, shared-pin full-duplex streams, ALSA control duplicate registration, and module debug logs for unexpected negative status transitions.
