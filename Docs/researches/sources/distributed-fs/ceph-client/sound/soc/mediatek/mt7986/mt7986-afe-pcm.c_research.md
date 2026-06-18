# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-afe-pcm.c

## Purpose

This is the MT7986 AFE platform driver. It registers DL1/VUL12 memif DAIs, combines them with ETDM, sets up bulk clocks, MMIO regmap with volatile registers, IRQ metadata, runtime PM, and platform binding for `"mediatek,mt7986-afe"`.

## Important APIs, Types, and Functions

- `mt7986_afe_rate_transform()` maps ALSA rates to MT7986 hardware values.
- `mt7986_memif_dai_driver[]`, `memif_data[]`, and `irq_data[]` describe FE DAIs, memory-interface registers, and IRQ registers.
- `mt7986_is_volatile_reg()` marks current pointers, monitor registers, and IRQ status volatile.
- `mt7986_init_clock()` uses `devm_clk_bulk_get()`.
- `mt7986_afe_irq_handler()` services enabled MCU IRQs.
- Runtime PM enables/disables bulk clocks and audio top/engine registers.
- `mt7986_afe_pcm_dev_probe()` maps resources, initializes regmap under temporary clock enable, registers ETDM/memif sub-DAIs, and registers ASoC components.

## Control Flow

Probe allocates `mtk_base_afe`, sets driver data early, maps MMIO, obtains bulk clocks, enables runtime PM, temporarily bypasses register control while clocks are on to initialize regmap defaults, then allocates memif/IRQ arrays and requests IRQ. It registers ETDM first, memif second, combines sub-DAIs, assigns common callbacks, and registers platform/DAI components. Runtime resume enables clocks and audio top/engine clocks; suspend disables register clocks, clears IRQ status, and disables bulk clocks. ISR filters status by MCU enable bits and memif IRQ usage before period notifications.

## State and Persistence Behavior

Persistent state includes bulk clocks, `pm_runtime_bypass_reg_ctl`, memif/IRQ arrays, sub-DAIs, and regmap cache. Volatile current/monitor/status registers bypass cache. Resume re-enables top clocks but stream-specific memif state is handled by common FE logic.

## Dependencies and Integration Points

Depends on DT MMIO/IRQ/clocks, `mt7986-reg.h`, ETDM registration, common MediaTek FE/platform helpers, and machine links using `DL1`, `UL1`, and `ETDM`.

## Risks and Edge Cases

`pm_runtime_get_sync()` return is not checked during regmap default capture. Runtime remove disables PM and may call suspend manually. Rate transform falls back to 48 kHz with warning for unsupported rates, but advertised rates limit most invalid input. IRQ handler clears only `status_mcu`, so invalid IRQs with no matching status clear zero.

## Test Signals

Probe with regmap default capture, playback/capture through DL1/UL1, ETDM BE activation, IRQ period delivery, runtime PM cycles, and regcache/volatile behavior through debugfs are key signals.
