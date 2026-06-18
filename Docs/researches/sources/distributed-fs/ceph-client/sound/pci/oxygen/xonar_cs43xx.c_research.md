
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_cs43xx.c

Purpose: board support for Xonar D1/DX cards using CS4398 front DAC, CS4362A multichannel DAC, CS5361 ADC, and CM9780 AC97 routing.

Important functions/types: `struct xonar_cs43xx` embeds `xonar_generic` and codec register caches. `cs4398_write*` and `cs4362a_write*` perform I2C writes and cache values. `cs43xx_registers_init` powers down, configures, and powers up both DACs. D1/DX init sets I2C speed, GPIO output/front-panel/input routes, CS53x1 ADC GPIOs, external power for DX, and component strings. Rate, volume, mute, center/LFE mix, front-panel switch, DAC rolloff, AC97 line/mic routing, and proc dump callbacks fill `model_xonar_d1`.

Control flow/state: Virtuoso model selection calls `get_xonar_cs43xx_model`; shared probe allocates model_data and calls init. Mixer operations update cached codec registers and GPIO. Resume resets codecs, replays caches, and enables output after delay.

Dependencies: Oxygen I2C/GPIO/AC97 helpers, Xonar generic helpers, CS4398/CS4362A/CM9780 constants, ALSA controls.

Risks: front and multichannel DACs must remain synchronized for rate/mute/filter; DX external power loss only logs TODO for stopping PCMs. Test signals: D1/DX probe, power event, 8-channel playback, front panel switch, rolloff, volume/mute, line/mic switching, capture, resume, and proc dumps.
