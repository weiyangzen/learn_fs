# sources/distributed-fs/ceph-client/sound/soc/sophgo/cv1800b-tdm.c

Purpose: ASoC CPU DAI driver for the Sophgo CV1800B I2S/TDM controller with DMAEngine PCM support.

Important APIs/functions: probe maps registers, records FIFO DMA addresses, enables `i2s` and `mclk` clocks, initializes TDM/DMA mode, registers a DAI cloned from `cv1800b_i2s_dai_template`, and registers DMAEngine PCM. DAI ops include startup trigger ordering, `hw_params()` slot/frame programming, MCLK/BCLK divider calculation, word-length programming, TX/RX mode selection, FIFO/I2S reset, trigger enable/disable, I2S-only format selection, fixed BCLK ratio, and sysclk output control. Remove disables I2S, audio clocks, MCLK output, and asserts reset bits.

Control flow/state: `struct cv1800b_i2s` stores MMIO, clocks, DMA data, optional configured MCLK rate, and optional fixed BCLK ratio. If no MCLK is supplied by the machine driver, the driver computes a 256fs MCLK and programs the common clock framework. Register state is reset during hw_params and disabled during remove.

Dependencies/integration: depends on CCF clocks named `i2s` and `mclk`, Device Tree compatible `sophgo,cv1800b-i2s`, DMAEngine PCM, and ASoC DAI format/sysclk callbacks.

Risks/test signals: only I2S format is accepted despite TDM naming; clock-rate mismatch logs but does not fail after `clk_set_rate`. BCLK divider uses rounded division and warns on misalignment, so audio clock accuracy should be measured. Tests should cover playback/capture, 16/24-bit formats, 8-192 kHz rates, master/slave formats, fixed BCLK ratio, sysclk output, DMA addresses, remove-time disable, and invalid slots/widths.
