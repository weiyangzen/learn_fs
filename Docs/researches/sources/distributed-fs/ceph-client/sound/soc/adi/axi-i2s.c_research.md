# sources/distributed-fs/ceph-client/sound/soc/adi/axi-i2s.c

## Purpose
`axi-i2s.c` is an ASoC CPU DAI driver for the Analog Devices AXI-I2S softcore. It registers playback and/or capture DAIs based on device-tree DMA names, programs frame clocking, controls TX/RX enables, and binds the generic DMAengine PCM backend to MMIO FIFO addresses.

## Important APIs, Types, And Functions
The main state is `struct axi_i2s`, containing regmap, AXI/ref clocks, capture/playback capability flags, DAI driver copy, DMA data, and rate constraints. Important functions include `axi_i2s_parse_of()`, `axi_i2s_probe()`, `axi_i2s_dev_remove()`, `axi_i2s_dai_probe()`, `axi_i2s_startup()`, `axi_i2s_shutdown()`, `axi_i2s_hw_params()`, and `axi_i2s_trigger()`.

## Control Flow
Probe allocates state, parses `dma-names` for `rx`/`tx`, maps registers, creates a 32-bit regmap, gets `axi` and `ref` clocks, enables the AXI clock, fills playback/capture DAI capabilities and DMA FIFO addresses for available directions, derives a rational rate constraint from the ref clock, globally resets the core, registers the ASoC component/DAI, and registers generic DMAengine PCM. PCM startup resets the selected FIFO, applies rate constraints, and enables the ref clock. `hw_params()` computes bit-clock rate for a fixed 64-bit frame and writes word size/divider. Trigger sets or clears TX/RX enable bits.

## State And Persistence
Persistent state lives in devm-managed `struct axi_i2s`, enabled clocks, regmap-visible core registers, DAI capabilities, and DMAengine configuration. PCM stream state is maintained by ASoC and DMAengine; this driver programs only core control and clocking.

## Dependencies And Integration Points
The driver integrates with OF compatible `adi,axi-i2s-1.00.a`, platform MMIO resources, named clocks `axi` and `ref`, `dma-names`, regmap MMIO, ASoC component/DAI registration, and generic DMAengine PCM.

## Risks And Edge Cases
`axi_i2s_dai` is a static template modified at probe time, which is risky if multiple instances with different capabilities probe. Divider calculation assumes a valid ref clock and can underflow if the requested rate exceeds feasible clocking. The frame size is fixed at 64 bits even though hardware is described as configurable. Remove disables only the AXI clock; stream shutdown handles ref clock balancing.

## Test Signals
Tests should cover playback-only, capture-only, and full-duplex DT nodes, missing clocks/resources, rate-constraint behavior, divider programming for supported rates, FIFO reset on startup, trigger enable/disable bits, DMA FIFO address correctness, and multiple-instance probing.
