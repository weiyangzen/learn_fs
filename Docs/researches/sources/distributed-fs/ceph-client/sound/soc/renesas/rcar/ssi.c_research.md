# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/ssi.c

## Purpose

`ssi.c` implements the Serial Sound Interface transport modules. It handles SSI clock master setup through ADG, serial format/register configuration, DMA and PIO transfer modes, IRQ handling, multi-SSI and shared-pin support, parent SSI clocking, DT parsing, and PIO fallback.

## Important APIs, types, and functions

`struct rsnd_ssi` stores module state, control-register fragments, word-select state, runtime channel/rate, IRQ, user count, and PIO pointer counters. Public helpers include `rsnd_ssi_use_busif()`, `rsnd_ssi_clk_query()`, `rsnd_ssi_multi_secondaries_runtime()`, `rsnd_ssi_is_dma_mode()`, `__rsnd_ssi_is_pin_sharing()`, `rsnd_parse_connect_ssi()`, and `rsnd_ssi_mod_get()`. Core callbacks include `rsnd_ssi_init()/quit()`, `rsnd_ssi_start()/stop()`, `rsnd_ssi_irq()`, `rsnd_ssi_hw_params()`, DMA probe/fallback, PIO init/pointer/interrupt, and common IRQ request/remove.

## Control Flow

Probe parses each `ssi-N` DT child, gets `ssi.N` clock and IRQ, records `shared-pin`, `no-busif`, and `pio-transfer`, then initializes modules in DMA or PIO mode. DT connection parsing fills the primary SSI slot and optional multi-SSI secondary slots, expanding DAI max channels and SSI lane count. At PCM creation, shared-pin clock parents can be attached. Init starts a master clock when needed, increments `usrcnt`, powers the module, builds SSICR/SSIWSR settings, writes registers, and clears status. Start enables SSI unless multi-SSI control is delegated to SSIU or the module is only a parent. Stop drains playback, disables SSI, and waits for idle. DMA probe attaches DMA; if DMA allocation fails with `-EAGAIN`, fallback switches ops to PIO and the core reprobes.

## State and Persistence Behavior

`usrcnt` protects shared clock/module state across parent/child and multi-path users. Register fragments (`cr_own`, `cr_clk`, `cr_mode`, `cr_en`, `wsr`) are rebuilt at init and cleared when the last user quits. PIO state (`byte_pos`, `byte_per_period`, `next_period_byte`) tracks software PCM position. Parent SSI lifecycle status is stored in the stream rather than the module to handle shared-pin full-duplex cases.

## Dependencies and Integration Points

SSI depends on ADG for master clock selection, SSIU for BUSIF and multi-SSI/TDM control, DMA for transfer attachment, core format/TDM/channel helpers, OF IRQ/DT parsing, and ASoC PCM runtime state. SSI interrupts also delegate BUSIF error clearing to SSIU.

## Risks and Test Signals

Risks include clock-rate search failures, shared-pin parent status imbalance, multi-SSI synchronization, TDM split fixed-width handling, PIO byte-position correctness, DMA-to-PIO fallback, and underflow/overflow handling. Tests should cover DMA and PIO playback/capture, full-duplex shared pins, multi-lane TDM, TDM split, 16/24/32-bit formats, clock-master and clock-consumer modes, IRQ xrun paths, and repeated trigger cycles.
