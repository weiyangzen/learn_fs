# sources/distributed-fs/ceph-client/sound/soc/au1x/ac97c.c

## Purpose
ASoC CPU DAI driver for the older Au1000/Au1500/Au1100 integrated AC97C controller. It implements AC97 bus read/write/reset operations, exposes a stereo playback/capture DAI, and passes legacy DMA request IDs to the Au1x PCM DMA component.

## Important APIs, Types, And Functions
- Uses `struct au1xpsc_audio_data` from `psc.h` for MMIO, config, mutex, and DMA IDs.
- `au1xac97c_ac97_read/write/warm_reset/cold_reset` implement `snd_ac97_bus_ops`.
- `alchemy_ac97c_startup()` attaches DMA IDs to substreams.
- `au1xac97c_drvprobe()` maps resources, reads DMA resources, powers the AC97C, registers AC97 ops and DAI component.
- PM handlers disable/restore the controller.

## Control Flow
Probe allocates context, maps MEM resource manually, stores playback/capture DMA resource IDs, enables the AC97 clock, configures front L/R slots, registers bus ops and the DAI. AC97 reads/writes poll command-pending bits with retries under a mutex. Cold reset toggles reset and waits for codec-ready. Startup associates DMA IDs; DAI probe depends on the global workdata pointer.

## State And Persistence
Global `ac97c_workdata` means only one controller instance is supported. `ctx->cfg` persists slot configuration across reset/resume. Runtime state is MMIO register state plus driver memory.

## Dependencies And Integration Points
Depends on MIPS Alchemy headers, ASoC AC97 bus support, the separate `alchemy-pcm-dma` component, and platform MEM/DMA resources. Platform driver name is `alchemy-ac97c`.

## Risks
Global singleton state is not multi-device safe. Manual MMIO request/ioremap paths are older than devm_platform helpers. Polling loops and errata timing are sensitive to hardware behavior. AC97 read failure returns `0xffff`, which can be confused with real register data.

## Test Signals
AC97 codec reset/read/write under load, DMA ID propagation to `dma.c`, suspend/resume restoring `ctx->cfg`, module unload clearing global workdata, and timeout/debug logs on missing codecs.
