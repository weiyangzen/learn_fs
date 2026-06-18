# sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio_olpc.c

Purpose: OLPC XO-1 board-specific extensions for CS5535 audio, handling analog input selection, microphone bias, and mixer control replacement around the AD1888 AC97 codec.

Important APIs and types: `olpc_analog_input` toggles AC97 high-pass-filter disable and `OLPC_GPIO_MIC_AC`; `olpc_mic_bias` manipulates AC97 `V_REFOUT` as mic bias. ALSA controls are `DC Mode Enable` and `MIC Bias Enable`. `olpc_prequirks` adjusts AC97 scaps for inverted EAPD on later boards; `olpc_quirks` requests/configures GPIO, removes generic controls, adds OLPC controls, and defaults mic bias off; `olpc_quirks_cleanup` frees GPIO.

Control flow: all entry points first check `machine_is_olpc` except cleanup. The core mixer path calls `olpc_prequirks` before AC97 mixer creation and `olpc_quirks` afterward. PCM capture open/close helpers in the header call `olpc_analog_input` and `olpc_mic_bias` to manage recording hardware state.

State and persistence: state is stored in GPIO output level and AC97 register bits. No persistent data; cleanup releases the GPIO line.

Dependencies and integration: depends on ALSA controls/info, AC97 AD-specific register fields, Linux GPIO API, and `asm/olpc.h`. It integrates only when `CONFIG_OLPC` is set.

Risks and test signals: `put` callbacks always return changed even if the requested state equals current state; GPIO request failure aborts mixer setup on OLPC machines. Test on OLPC and non-OLPC boot paths, control add/remove behavior, capture open/close LED/mic-bias side effects, and GPIO cleanup during card free.
