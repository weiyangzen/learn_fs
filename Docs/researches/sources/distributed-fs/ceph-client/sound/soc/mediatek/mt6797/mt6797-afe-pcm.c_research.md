# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-pcm.c

## Purpose

This is the MT6797 AFE platform driver. It defines rate mappings, PCM hardware constraints, FE memif DAIs, DAPM routes for capture memory interfaces, memif/IRQ register metadata, IRQ handling, runtime PM register programming, sub-DAI combination, and platform driver binding.

## Important APIs, Types, and Functions

- `mt6797_general_rate_transform()` and `mt6797_rate_transform()` convert ALSA rates to hardware values.
- `mt6797_memif_dai_driver[]` exposes DL1-DL3, UL1-UL3, and two mono capture DAIs.
- `memif_data[]` maps base/current/end, fs, mono, enable, and HD fields for each memif.
- `irq_data[]` maps IRQ counters, fs fields, enable fields, and clear bits.
- `mt6797_afe_irq_handler()` handles enabled MCU IRQ status and calls `snd_pcm_period_elapsed()`.
- Runtime PM functions enable/disable clocks, AFE, IRQ routing, HD alignment, and 24-bit connections.
- `mt6797_afe_pcm_dev_probe()` allocates state, MMIO regmap, memifs/IRQs, requests IRQ, registers ADDA/PCM/hostless/memif sub-DAIs, combines them, and registers ASoC components.

## Control Flow

Probe initializes clocks first, maps MMIO, creates regmap, allocates memif and IRQ arrays, requests the platform IRQ, builds `afe->sub_dais` through the registration callback array, combines sub-DAIs, assigns common callbacks, enables runtime PM, and registers platform plus DAI components. Runtime resume enables clocks, routes IRQs to the MCU, sets normal/8_24 data modes, marks output connections as 24-bit, and turns on AFE. Runtime suspend clears AFE on, waits for retention to drop, clears pending IRQs, and disables clocks. ISR reads MCU enable/status, filters active bits, services memifs with substreams, and clears status.

## State and Persistence Behavior

State resides in `afe->memif`, `afe->irqs`, `afe->sub_dais`, and `mt6797_afe_private.clk`. No register backup list is configured; runtime resume reprograms key global format/IRQ/AFE state. Memif substream and IRQ usage state is managed by common FE helpers.

## Dependencies and Integration Points

Depends on MMIO resources, platform IRQ, `mt6797-reg.h`, clock helpers, ADDA/PCM/hostless sub-DAI registration, common MediaTek FE/platform helpers, and machine drivers that consume the registered DAI names.

## Risks and Edge Cases

Unsupported rates fall back to 48 kHz or 16 kHz with warnings rather than hard failure in transform helpers. Probe's PM-runtime-disabled path jumps to `err_pm_disable` with `ret` still zero after `pm_runtime_enable()` succeeds but runtime PM is unavailable. Clock enable currently risks swallowing failures through the clock file. ISR assumes `irq_usage` is valid whenever `substream` is set.

## Test Signals

Boot/probe with IRQ and MMIO resources, run playback on DL1-DL3, capture on UL and mono DAIs, test ADDA/PCM/hostless machine routes, verify period interrupts, and exercise runtime PM with regmap traces.
