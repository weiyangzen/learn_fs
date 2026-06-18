# sources/distributed-fs/ceph-client/sound/soc/codecs/88pm860x-codec.h

Purpose: register and public-helper header for the 88PM860x ASoC codec driver. It provides symbolic register addresses, clock direction constants, detection mask constants, and jack-detection helper prototypes for machine drivers.

Important APIs, types, and functions: defines audio interface, gain, ADC/DAC, analog, supply, calibration, and input-select register addresses from `PM860X_PCM_IFACE_1` through `PM860X_I2S_IFACE_5`, plus `PM860X_SHORTS` and PLL adjustment registers. Defines `PM860X_CLK_DIR_IN/OUT`, detection bits `PM860X_DET_HEADSET`, `PM860X_DET_MIC`, `PM860X_DET_HOOK`, `PM860X_SHORT_HEADSET`, `PM860X_SHORT_LINEOUT`, and `PM860X_DET_MASK`. Declares `pm860x_hs_jack_detect()` and `pm860x_mic_jack_detect()`.

Control flow: none; the header is a compile-time contract.

State and persistence: no state in the header. Constants map to hardware state managed by `88pm860x-codec.c`.

Dependencies and integration: included by codec implementation and by board/machine drivers that need jack detection helpers or PM860x constants. Depends on ALSA `struct snd_soc_component` and `struct snd_soc_jack` declarations being visible at use sites.

Risks: the include guard name starts with digits after the double underscore prefix, which is tolerated by preprocessors but is not a style ideal. Register constants must remain synchronized with PMIC documentation and MFD regmap coverage.

Test signals: compile codec and any machine driver using jack helpers; verify exported symbols resolve and detection masks match ALSA jack report expectations.
