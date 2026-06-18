# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo.h

Purpose: Declares the shared AIU FIFO state structure and operation prototypes used by the I2S and SPDIF FIFO variants.

Important APIs and types: `struct aiu_fifo` carries the PCM hardware description, register memory offset, FIFO burst/block size, pclk, and IRQ. Prototypes cover DAI probe/remove, pointer, trigger, prepare, hw_params, startup, shutdown, and `pcm_new`.

Control flow: No executable logic. The header defines the call contract for variant files to compose their `snd_soc_dai_ops` from common FIFO helpers.

State and persistence: Declares the shape of per-DAI playback DMA data allocated by `aiu_fifo_dai_probe()`.

Dependencies and integration points: Included by `aiu.c`, `aiu-fifo.c`, `aiu-fifo-i2s.c`, and `aiu-fifo-spdif.c`. Forward declarations avoid pulling in full ALSA headers in every include site.

Risks: The common helper contract is playback-only; using it for capture would require new DMA-data accessors and pointer semantics. Any change to `struct aiu_fifo` must be reflected in both variant probes.

Test signals: Build coverage for AIU FIFO variants and module link checks for all declared helper functions.
