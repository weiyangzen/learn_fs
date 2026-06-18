# sources/distributed-fs/ceph-client/include/sound/pcm_iec958.h

Source read summary: 20 lines, IEC958 channel-status helper for PCM.

Purpose: declares a helper for filling AES/IEC958 status bytes from PCM runtime parameters.

Important APIs, types, and functions: `snd_pcm_create_iec958_consumer()` takes a runtime, output status buffer, length, and optional AES0 non-audio flag override.

Control flow: SPDIF/HDMI drivers call the helper after hw_params/runtime setup to generate consumer channel-status bits matching sample rate, format, and audio/non-audio mode.

State and persistence behavior: no state is stored. The generated status bytes are used by caller hardware/register programming.

Dependencies and integration points: depends on ALSA PCM runtime and IEC958/asound definitions through users. Integrates PCM params with digital audio transmitters.

Risks and edge cases: incorrect status bits can make sinks reject audio; buffer length must match expected IEC958 status size; compressed/non-audio formats need correct AES0 handling.

Test signals: status generation for common sample rates/formats, non-audio streams, short buffer handling, and HDMI/SPDIF playback validation.
