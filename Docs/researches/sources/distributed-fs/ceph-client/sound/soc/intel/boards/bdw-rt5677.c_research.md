# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bdw-rt5677.c

## Purpose
This Broadwell machine driver supports RT5677 codec designs, including speaker/headphone routing, GPIO-based jack and headphone amplifier control, SSP0 audio, and a non-DPCM SPI wake-on-voice DSP capture path.

## Important APIs, Types, and Functions
`struct bdw_rt5677_priv` holds the headphone-enable GPIO and codec component. `bdw_rt5677_event_hp()` delays on headphone power-up and toggles the external headphone amplifier GPIO. `bdw_rt5677_init()` installs ACPI GPIO mappings, selects ASRC clocks with `rt5677_sel_asrc_clk_src()`, requests `headphone-enable`, creates headphone and mic jacks, attaches GPIO detection through `snd_soc_jack_add_gpios()`, and force-enables `MICBIAS1`. `bdw_rt5677_dsp_hw_params()` configures PLL/sysclk for the wake-on-voice link. Suspend/resume callbacks disable and re-enable `MICBIAS1`.

## Control Flow and Integration
The card defines a DPCM FE (`System PCM`), a capture-only `Codec DSP` link using `spi-RT5677AA:00` and `rt5677-dspbuffer`, and an SSP0 BE using `i2c-RT5677CE:00`/`rt5677-aif1`. `broadwell_ssp0_fixup()` forces 48 kHz stereo S16_LE. Probe mirrors the Broadwell pattern: fix platform names, choose SOF or legacy naming, set driver data, and register the card.

## State, Persistence, and Dependencies
State includes jack objects, GPIO descriptors, codec component pointer, and DAPM MICBIAS state. Persistent hardware effects are ACPI GPIO mappings, headphone amp GPIO state, codec ASRC/sysclk/PLL setup, and jack GPIO registration. Dependencies include RT5677 codec helpers, GPIOLIB/ACPI GPIO resources, SPI RT5677 DSP support, ASoC DPCM, and Broadwell platform audio.

## Risks and Test Signals
Risks include fragile GPIO index assumptions, leaking or double-freeing GPIOs if `.exit()` paths change, MICBIAS staying enabled across suspend transitions, and wake-on-voice SPI path dependency on a separate platform device. Test signals include both jack GPIOs reporting correctly, headphone amp toggling with DAPM, wake-on-voice capture device registration, SSP0 48 kHz stereo operation, and clean suspend/resume with MICBIAS restored.
