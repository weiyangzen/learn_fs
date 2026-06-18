# sources/distributed-fs/ceph-client/sound/soc/codecs/audio-iio-aux.c

Purpose: platform ASoC auxiliary component that exposes IIO raw channels as ALSA mixer controls and simple DAPM input-PGA-output paths. It lets machine drivers route analog or control-like IIO devices into an audio graph without a custom codec driver per device.

Important APIs and types: `struct audio_iio_aux_chan` holds an `iio_channel`, ALSA control name, raw min/max, and invert flag. `struct audio_iio_aux` stores the device and a counted flexible array of channels. ALSA callbacks `audio_iio_aux_info_volsw`, `audio_iio_aux_get_volsw`, and `audio_iio_aux_put_volsw` report range/type, read raw values, validate and write raw values. `audio_iio_aux_add_controls` creates one mixer control per channel; `audio_iio_aux_add_dapms` creates three widgets and two routes per channel.

Control flow: platform probe counts `io-channel-names`, allocates channel state, reads names and optional `snd-control-invert-range`, obtains each IIO channel by name, stores drvdata, and registers an ASoC component. Component probe reads each channel min/max, swaps inconsistent bounds defensively, writes the initial raw value to min or max depending on inversion, then adds the ALSA control and DAPM route.

State and persistence: state is devm-managed and lasts for the platform device lifetime. Channel raw values are persisted only in the underlying IIO provider/device. On component bind, this driver forces each channel to an initial endpoint, so prior hardware state is overwritten.

Dependencies and integration points: depends on platform devices/DT or firmware properties, IIO consumer APIs, ASoC component/control/DAPM APIs, string helper `str_on_off`, and devm allocation/lifetime. The compatible is `audio-iio-aux`.

Risks: `widgets` and `routes` are global scratch arrays. The comment relies on ASoC copying them under card bind locking; concurrent or future API changes could make this unsafe. Control names point at entries from the local `names` array returned by property reading; this is safe only because firmware property strings remain valid beyond probe. Initial writes can have side effects on hardware-controlled channels. Inversion math is simple and assumes raw values map linearly to ALSA integer values.

Test signals: instantiate with multiple `io-channel-names`; verify ALSA controls expose correct integer/boolean ranges; test inverted and non-inverted get/put paths; check DAPM widget/route names; simulate min greater than max; verify probe failure on missing channels and write failures; exercise unbind/rebind for devm cleanup.
