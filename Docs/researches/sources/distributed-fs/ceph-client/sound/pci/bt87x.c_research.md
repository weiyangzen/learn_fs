# sources/distributed-fs/ceph-client/sound/pci/bt87x.c

## Purpose

`bt87x.c` is an ALSA capture driver for Brooktree Bt878/Bt879 audio functions, commonly found on TV/video capture cards. It exposes analog and/or digital capture PCM devices depending on board metadata, creates a Bt87x RISC DMA program for scatter-gather audio capture, manages capture input controls for analog boards, and filters unsupported DVB/no-audio boards unless `load_all` is requested.

## Important APIs, Types, and Functions

`struct snd_bt87x` stores card, PCI device, MMIO base, IRQ, spinlock, single-open state, active substream, allocated RISC DMA buffer, current period geometry, cached audio control register, interrupt mask, current line/period, and parity error count.

Board behavior is described by `struct snd_bt87x_board`, with digital sample rate, digital format bits, and analog/digital disable flags. Static board tables cover known Hauppauge, Osprey, ATI, Leadtek, Pinnacle, AVerMedia, and related devices, while a denylist blocks known DVB/no-audio cards.

Key functions include `snd_bt87x_create_risc()` for building the hardware RISC instruction loop, `snd_bt87x_interrupt()` for error and period IRQ handling, `snd_bt87x_pcm_open()/close()`, `snd_bt87x_hw_params()/hw_free()`, `snd_bt87x_prepare()`, `snd_bt87x_start()/stop()`, and `snd_bt87x_pointer()`. Mixer-like capture controls are implemented through capture volume, boost, and source get/put callbacks.

Probe flows through `snd_bt87x_detect_card()`, `snd_bt87x_create()`, `__snd_bt87x_probe()`, and `snd_bt87x_probe()`. Module init optionally swaps the PCI ID table to default catch-all Bt878/Bt879 IDs when `load_all` is set.

## Control Flow

Initialization registers a PCI driver. Probe detects board identity using explicit PCI subsystem matches or the denylist. It allocates an ALSA card, maps BAR0 MMIO, initializes `REG_GPIO_DMA_CTL`, disables/clears interrupts, requests a shared IRQ, enables bus mastering, copies board configuration, creates digital and/or analog PCM capture devices, adds analog capture controls if analog is present, names the card, and registers it.

PCM open is exclusive via `test_and_set_bit()` on `chip->opened`. Digital open fixes rate to the board's digital rate and powers down analog input; analog open configures rational-rate constraints using the 1.792 MHz analog clock divider. HW params allocate/build the RISC program, splitting each period across page boundaries as needed. Prepare programs decimation and 8-bit rounding for analog capture formats.

Start writes the RISC program address, packet length, interrupt mask, and enables FIFO/RISC/audio capture. The RISC program raises `RISC_IRQ` at each period end and uses status bits to identify progress. The interrupt handler acknowledges masked status, logs FIFO and PCI/RISC errors, updates `current_line`, compensates for skipped interrupts by comparing status block bits, and calls `snd_pcm_period_elapsed()`.

## State and Persistence Behavior

Runtime state is volatile and hardware-backed. `reg_control` caches `REG_GPIO_DMA_CTL` so controls and stream state can safely update bit fields. `interrupt_mask` may be modified if repeated parity errors force parity interrupt disable. `current_line`, `line_bytes`, and `lines` track the DMA period position. The RISC DMA buffer is allocated lazily and freed on `hw_free`. There is no suspend/resume implementation in this file.

## Dependencies and Integration Points

The driver integrates with ALSA core, PCM, control APIs, PCI, Linux interrupt handling, MMIO accessors, scatter-gather PCM helpers, and PCI status error helpers. It uses `snd_pcm_set_managed_buffer_all()` with `SNDRV_DMA_TYPE_DEV_SG` for capture buffers and manual `snd_dma_alloc_pages()` for the RISC program.

## Risks and Edge Cases

The driver supports only one open capture stream at a time even if both analog and digital devices exist. Unknown cards default to guessed 32 kHz digital behavior unless blocked or configured. RISC program sizing assumes documented period and page-boundary limits. PCI parity errors can be observed from other bus devices; the driver disables parity-related interrupts after too many events. Analog sample rates depend on divider constraints and optional overclock configuration.

## Test Signals

Test with known board IDs and with unknown/denylisted cards. Validate analog capture at allowed rational rates and formats, digital capture at board or `digital_rate` fixed rates, exclusive-open enforcement, RISC DMA across page boundaries, period interrupt cadence, pointer monotonicity, capture volume/boost/source controls, FIFO overrun logging under stress, and parity error throttling behavior.
