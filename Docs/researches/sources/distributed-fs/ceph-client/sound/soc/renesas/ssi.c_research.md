# sources/distributed-fs/ceph-client/sound/soc/renesas/ssi.c

Purpose: Legacy SuperH SH7760/SH7780 SSI I2S CPU DAI driver. It directly controls SSI registers for simplex playback or capture, including sample width, channel count, clock divider, bus format, and DMA enable.

Important APIs, types, and functions: `struct ssi_priv` stores hard-coded MMIO base, requested sysclk, and an `inuse` simplex guard. Main DAI ops are `ssi_startup`, `ssi_shutdown`, `ssi_trigger`, `ssi_hw_params`, `ssi_set_sysclk`, `ssi_set_clkdiv`, and `ssi_set_fmt`. `sh4_ssi_dai` exposes one or two DAIs depending on CPU subtype. Probe registers `sh4_ssi_component`.

Control flow: Startup rejects concurrent use of the same SSI. `hw_params` computes CR bits for direction, even channel count 2-8, data word length, and system word length. `set_fmt` programs I2S/left/right-justified mode, gated clock, inversion, and clock-provider bits. Trigger START sets DMA and enable bits; STOP clears them. There is no IRQ or DMA descriptor handling here; a separate platform PCM driver is expected.

State and persistence: Driver state is static per SoC DAI. Register writes persist until overwritten. `sysclk` is cached but not used to compute dividers. `inuse` is not protected by a lock.

Dependencies and integration: Depends on compile-time SuperH CPU subtype, raw MMIO, ALSA SoC DAI registration, and external board code for pinmux and clock source setup.

Risks and edge cases: Hard-coded physical register addresses and raw dereferences are fragile. Simplex exclusion has a FIXME about locking and can race. Several switch statements intentionally fall through to encode bitfields; maintainers must preserve that pattern. No runtime PM, reset, or pinctrl integration exists.

Test signals: Loading should register `ssi-dai.0` and maybe `ssi-dai.1`. Invalid odd channels or unsupported sample widths should fail. START/STOP should toggle CR_DMAEN/CR_EN. Board tests should verify pinmux and external bit clock configuration separately.
