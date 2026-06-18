# sources/distributed-fs/ceph-client/sound/soc/qcom/sdw.h

Purpose: declares the Qualcomm shared SoundWire helper API used by several machine drivers.

Important APIs: `qcom_snd_sdw_startup()` allocates/binds streams. `qcom_snd_sdw_prepare()` prepares/enables a stream using a caller-owned prepared flag. `qcom_snd_sdw_get_stream()` returns the stream runtime for a substream. `qcom_snd_sdw_shutdown()` releases it. `qcom_snd_sdw_hw_free()` disables/deprepares it and clears the prepared flag.

Control flow and state: no state is stored here. The API makes machine drivers responsible for storing one prepared flag per CPU DAI ID and calling helpers in the ASoC startup/prepare/hw_free/shutdown sequence.

Dependencies and integration: includes `<linux/soundwire/sdw.h>` and is consumed by Qualcomm SoC machine drivers (`sdm845`, `sc7280`, `sc8280xp`, `sm8250`, `x1e80100`).

Risks: the header does not provide stubs, so Kconfig/build dependencies must ensure implementation availability. The `qcom_snd_sdw_get_stream()` parameter name is `stream` but type is substream, a minor readability hazard.

Test signals: all machine-driver users link when SoundWire support is enabled, and callback sequences consistently clear caller-owned prepared flags on hw_free.
