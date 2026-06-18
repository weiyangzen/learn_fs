# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-lpass-ports.h

Purpose: this header defines the narrow configuration interface used by Qualcomm QDSP6 LPASS audio-port DAI registration code. It does not implement runtime behavior; it lets a platform component provide DAI operation tables for HDMI, Slimbus, I2S, TDM, DMA, and USB backends and receive an array of `snd_soc_dai_driver` definitions.

Important APIs and types: `struct q6dsp_audio_port_dai_driver_config` carries optional `probe`/`remove` callbacks and per-transport `snd_soc_dai_ops` pointers. `q6dsp_audio_ports_set_config()` builds/configures the DAI driver list for a device and returns both the array and DAI count. `q6dsp_audio_ports_of_xlate_dai_name()` translates OF phandle args into ASoC DAI names for components.

Control flow and state: no state is stored here. Callers allocate/fill a config, pass it to the implementation, then register the returned DAIs with ASoC. Runtime callback behavior is delegated through the ops pointers.

Dependencies and integration: depends on ASoC core declarations (`snd_soc_dai`, `snd_soc_component`, `of_phandle_args`) and is consumed by QDSP6 audio port platform drivers such as USB and generic LPASS backend registration.

Risks: all fields are raw callback pointers, so missing or mismatched ops cause late runtime failures. The API also exposes the returned DAI array lifetime implicitly through the implementation.

Test signals: build coverage for all enabled backend transports, DT phandle DAI-name lookup tests through card probing, and boot-time ASoC registration logs for every configured LPASS backend.
