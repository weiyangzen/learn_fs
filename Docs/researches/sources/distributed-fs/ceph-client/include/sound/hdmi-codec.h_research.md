# sources/distributed-fs/ceph-client/include/sound/hdmi-codec.h

Source read summary: 140 lines, ASoC HDMI codec platform API.

Purpose: defines the protocol between an ASoC CPU DAI/codec wrapper and an HDMI encoder/display driver for I2S or SPDIF audio.

Important APIs, types, and functions: `struct hdmi_codec_daifmt` describes DAI format, clock inversion/provider roles, and PCM/IEC958 bit format. `struct hdmi_codec_params` carries HDMI infoframe, IEC958 channel status, sample rate, sample width, and channel count. `hdmi_codec_plugged_cb` reports connector state. `struct hdmi_codec_ops` provides optional startup, mandatory `hw_params` or `prepare`, mandatory shutdown, optional mute, ELD fetch, DAI ID mapping, and plugged callback hook. `struct hdmi_codec_pdata` advertises I2S/SPDIF capabilities, capture/playback suppression, max I2S channels, and opaque encoder data.

Control flow: machine/encoder code registers a platform device with pdata; ASoC stream startup calls the encoder ops to configure infoframes and audio format, mutes/unmutes as needed, and shuts down at stream close. Hotplug can be forwarded through the callback.

State and persistence behavior: no state is stored in the header; runtime state lives in the codec driver, encoder private data, and connector/ELD cache.

Dependencies and integration points: includes OF graph, HDMI infoframes, ALSA IEC958/asound definitions, and ASoC. It connects SoC audio cards to DRM/display HDMI encoders.

Risks and edge cases: exactly one of prepare/hw_params must be supplied, ELD length and hotplug callback lifetime must be respected, and I2S/SPDIF capability flags must match DAI registrations.

Test signals: ASoC card probe, I2S and SPDIF stream startup/shutdown, IEC958 and infoframe contents, ELD read on hotplug, mute behavior, DAI endpoint ID mapping, and capture-disabled configurations.
