# sources/distributed-fs/ceph-client/sound/soc/sophgo/cv1800b-sound-adc.c

Purpose: ASoC codec driver for the internal CV1800B/SG2002 RXADC capture block.

Important APIs/functions: `cv1800b_adc_probe()` maps registers and registers the component/DAI. `cv1800b_adc_dai_set_sysclk()` stores the external MCLK rate. `cv1800b_adc_hw_params()` programs the BCLK divider and ADC decimation/init bits for the requested capture rate. `cv1800b_adc_dai_trigger()` enables/disables RXADC and I2S TX on PCM trigger. Volume controls use `cv1800b_adc_volume_get()`/`set()` with a 0-48 dB, 2 dB step TLV scale and a hardware gain lookup table.

Control flow/state: `struct cv1800b_priv` stores MMIO base, device, and MCLK rate. Hardware register state persists across stream opens until overwritten. Capture DAI is fixed to up to two channels, 48 kHz, S16_LE.

Dependencies/integration: integrates with ASoC component/DAI registration and Device Tree compatible `sophgo,cv1800b-sound-adc`. Usually paired with the CV1800B TDM CPU DAI.

Risks/test signals: BCLK divider depends on machine driver calling `set_sysclk`; missing MCLK yields `-EINVAL`. The gain getter decodes bit masks by first-set-bit and may not exactly invert arbitrary register values. Tests should cover DT probe, sysclk absence/presence, 48 kHz capture, trigger enable/disable, volume get/set for both channels, and invalid divider ranges.
