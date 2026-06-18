# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/src.c

## Purpose

`src.c` implements the Sampling Rate Converter module. It configures SRC hardware for fixed or DPCM-derived rate conversion, exposes optional synchronous conversion controls, manages SRC interrupts, attaches DMA, and provides converted-rate helpers used by SSI/ADG/CMD.

## Important APIs, types, and functions

`struct rsnd_src` stores the module, DMA module, synchronous-conversion enable/rate controls, current sync rate, and IRQ. `rsnd_src_get_rate()` reports input or output rate based on stream direction and conversion state. `rsnd_src_init_convert_rate()` calculates register settings for ADINR, IFSCR, SRCCR, route mode, BSDSR/BSISR, BUSIF mode/alignment, and ADG timesel. `rsnd_src_set_convert_rate()` updates `SRC_IFSVR` gradually in synchronous mode. `rsnd_src_irq()`, `rsnd_src_error_occurred()`, and `rsnd_src_interrupt()` manage overflow/underflow status. `rsnd_src_pcm_new()` registers `SRC In/Out Rate Switch` and `SRC In/Out Rate` controls when supported. `rsnd_src_probe()` allocates modules, IRQs, clocks, and ops.

## Control Flow

Probe creates SRC modules from the `rcar_sound,src` node. During stream probing, `rsnd_src_probe_()` requests an IRQ if available and attaches DMA. At init, SRC clears synchronous conversion state, powers on, activates, computes conversion settings from runtime and DPCM metadata, writes registers, sets ADG timesel, and clears status. Start writes `SRC_CTRL`, with a workaround for DVC plus non-sync conversion. IRQ enable writes per-SRC interrupt bits unless no IRQ or disabled. Interrupts scan all streams using the module and stop the PCM on SRC error after clearing status.

## State and Persistence Behavior

Synchronous conversion controls persist in `sen` and `sync`, but `sync.val` and `current_sync_rate` are reset on init/quit. `current_sync_rate` avoids redundant `SRC_IFSVR` writes and tracks gradual runtime adjustments. DMA module state is retained in `src->dma` after first attachment.

## Dependencies and Integration Points

SRC depends on ADG timing, DMA attachment, common channel/data-alignment helpers, ALSA controls, DPCM conversion metadata from `core.c`, SCU pseudo registers, and optional CMD/DVC interactions. It is a central rate-conversion module in both playback and capture paths.

## Risks and Test Signals

Risks include SRC ratio limits, channel-pattern tables that vary by SRC ID and E3 SoC variant, synchronous-conversion overflow workaround behavior, runtime control updates while streaming, and DPCM BE/FE mismatch handling. Tests should cover no-conversion, upsample/downsample, DPCM converted rate/channel, synchronous rate-control updates, SRC interrupt error handling, and unsupported channel/rate combinations.
