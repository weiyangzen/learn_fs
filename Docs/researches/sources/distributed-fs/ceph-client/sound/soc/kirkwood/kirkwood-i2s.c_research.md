# sources/distributed-fs/ceph-client/sound/soc/kirkwood/kirkwood-i2s.c

## Purpose
Implements the Kirkwood/Dove/Armada I2S and SPDIF CPU DAIs, including rate-source selection, Armada 38x PLL quirks, stream format setup, and trigger control.

## Important APIs, Types, And Functions
Important routines include `armada_38x_i2s_init_quirk()`, `armada_38x_set_pll()`, `kirkwood_i2s_set_fmt()`, `kirkwood_set_dco()`, `kirkwood_set_rate()`, `kirkwood_i2s_hw_params()`, playback/capture trigger helpers, `kirkwood_i2s_init()`, and `kirkwood_i2s_dev_probe()`. It registers two DAIs, `i2s` and `spdif`, with either fixed-rate or external-clock continuous-rate capabilities.

## Control Flow, State, And Persistence
Probe maps registers, gets IRQ and clocks, applies Armada 380 named-resource quirks, chooses burst size, optionally enables an external clock, initializes cached playback/record control words, registers the shared PCM component, and places hardware into a safe state. `hw_params` sets PLL/DCO/extclk rate, word-size bits, mono behavior, and I2S/SPDIF enable bits cached in `ctl_play` and `ctl_rec`. Trigger handlers write pause/mute/enable and interrupt mask bits.

## Dependencies And Integration Points
Depends on DT compatibles `marvell,kirkwood-audio`, `marvell,dove-audio`, `marvell,armada370-audio`, and `marvell,armada-380-audio`, optional platform data, internal/ext clocks, MBUS-era MMIO layout, and `kirkwood_soc_component` from `kirkwood-dma.c`.

## Risks And Test Signals
Risks include an unbounded busy wait in DCO lock, fixed magic initialization of register `0x1200`, external-clock rate failures not propagated, Armada 38x named resource requirements, and distinct I2S/SPDIF enable masking on shared control registers. Test signals include I2S and SPDIF playback/capture, 44.1/48/96/192 kHz rates, external-clock and internal DCO paths, Armada 380 SPDIF-mode DT property, and trigger stop/start without DMA underruns.
