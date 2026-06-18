# sources/distributed-fs/ceph-client/sound/soc/stm/stm32_i2s.c

Purpose: STM32 SPI/I2S block ASoC DAI driver with full-duplex playback/capture, dmaengine PCM, regmap-backed MMIO, optional MCLK provider, and clock-parent management for 8 kHz and 11.025 kHz rate families.

Important APIs and types: `struct stm32_i2s_data` stores regmap, clocks, DMA data, substream, MMIO/physical address, full-duplex and IRQ locks, MCLK/divider state, format/master flags, refcount, and clock-rate strategy hooks. `struct stm32_i2s_conf` supplies regmap config and optional parent-clock lookup. DAI ops implement probe, set_sysclk, set_fmt, startup, hw_params, trigger, and shutdown. MCLK `clk_ops` derive and program I2S prescalers.

Control flow: probe parses DT, maps MMIO, gets clocks, optional reset and IRQ, optionally registers an MCLK provider, initializes regmap, registers dmaengine PCM and ASoC component, enables I2S mode, checks hardware capability/version, and enables PM. `set_fmt()` programs protocol, inversion, and master/slave mode. `set_sysclk()` handles MCLK output in master mode, requesting exclusive clock rates and enabling MCK output. `hw_params()` configures data length/channel length/master/slave mode and, in master mode, calculates/programs clock dividers. Trigger start enables DMA bits, SPE/CSTART, clears interrupts, increments full-duplex refcount, and enables underrun/overrun/frame-error interrupts. Trigger stop disables the stream interrupt, decrements refcount, and only disables I2S/DMA when the last full-duplex stream stops. IRQ clears active flags and stops the stream on overrun/underrun.

State and persistence: regmap cache is used over system sleep. `refcount` protects full-duplex shared hardware enable. `i2s_clk_flg` tracks exclusive parent clock ownership. `mclk_rate`, `div`, `odd`, and `divider` store prescaler state.

Dependencies and integration points: compatibles `st,stm32h7-i2s` and `st,stm32mp25-i2s`, clocks `pclk`, `i2sclk`, optional `x8k`/`x11k`, optional `#clock-cells`, reset, IRQ, dmaengine PCM, regmap MMIO, and ASoC DAI machine-driver format/sysclk calls.

Risks: stop paths use `regmap_update_bits(..., mask, (unsigned int)~mask)` when clearing interrupt bits; update_bits masks the value, but this is non-obvious and fragile. In full-duplex, one `substream` pointer is shared for IRQ XRUN reporting, so the last startup wins. Clock exclusivity must be released on all failure/shutdown paths. MCLK name construction strips after `_` and may collide. Slave mode still uses shared full-duplex mode settings.

Test signals: master/slave I2S, left/right justified and DSP_A formats, 16/32-bit, playback/capture/full-duplex, MCLK provider consumers, 8k and 11.025k families, clock failure unwinding, IRQ overrun/underrun, suspend/resume regcache sync, and repeated start/stop refcount balance.
