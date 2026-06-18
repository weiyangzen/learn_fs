# sources/distributed-fs/ceph-client/sound/soc/renesas/fsi.c

Purpose: full Renesas/SuperH Fifo-attached Serial Interface ASoC component/DAI driver for FSI1/FSI2, supporting playback/capture on ports A/B, PIO and DMAEngine transfer, clock setup, SPDIF mode, runtime PM, and suspend/resume.

Important types and functions: `struct fsi_stream` tracks substream, FIFO/buffer capacities, sample positions, period progress, bus options, error counters, handler, and DMA channel. `struct fsi_priv` represents one FSI port; `struct fsi_master` owns common registers and two ports. Handler tables implement PIO push/pop and DMA push. DAI ops include `fsi_dai_trigger()`, `fsi_dai_set_fmt()`, and `fsi_dai_hw_params()`. Probe initializes ports, parses OF/platform flags, requests IRQ, and registers two DAIs.

Control flow: probe determines FSI core version, maps registers, initializes port A/B, selects DMA or PIO handlers, enables runtime PM, requests IRQ, and registers component/DAIs. Startup invalidates clock; set_fmt configures master/slave, inversion, clock source, and PCM/I2S/SPDIF format. hw_params validates clock rate for master mode. Trigger start initializes stream, configures hardware/FIFO/clock, starts handler, and primes transfer; stop shuts down clock, stops handler, and logs FIFO errors. IRQ dispatch transfers active streams and clears error/status bits.

State and persistence: all runtime state is in `fsi_master`/`fsi_priv`/`fsi_stream`: register bases, clock handles/rates/counts, format flags, DMA channels, buffer positions, and error counters. No persistent configuration beyond DT/platform flags.

Dependencies and integration: depends on clocks, DMAEngine or SH DMA filters, OF match `renesas,sh_fsi`/`renesas,sh_fsi2`, platform data `sh_fsi`, ASoC PCM/DAI APIs, and simple-card users.

Risks: complex clock-rate search and ACK/BPF programming; mixed spinlock and runtime callbacks; DMA fallback recursively probes PIO handlers; capture DMA overflow workaround is noted as FIXME; only playback DMA handler is registered; several assumptions are tied to FSI2 register layout.

Test signals: PIO playback/capture interrupts, DMA playback fallback/success, clock master external/CPG rates at 44.1/48 kHz families, suspend/resume while streams active, FIFO over/under error accounting, SPDIF FSI2 output, and OF/platform-data probe paths.
