# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6routing.c

Purpose: implements the legacy Q6ADM routing component that connects ALSA front-end MultiMedia streams to QDSP6 backend AFE ports through DAPM mixers and ADM COPP matrix mapping.

Important APIs and functions: exported APIs are `q6routing_stream_open()` and `q6routing_stream_close()`. `routing_hw_params()` records backend port format in `port_data`. `msm_routing_get_audio_mixer()` and `msm_routing_put_audio_mixer()` implement mixer controls that assign a frontend session to a backend port. `q6pcm_routing_probe()` registers the ASoC component.

Control flow: probe allocates global `routing_data`, initializes sessions to invalid IDs during component probe, and registers a component containing a large static DAPM graph. Userspace mixer changes set `session->port_id`. During stream open, the driver copies the selected backend format into the frontend session, opens a COPP with `q6adm_open()`, stores it by COPP index in `copp_map`, then calls `q6adm_matrix_map()` to connect session and port. Close finds the session by frontend DAI ID and closes all COPPs.

State and persistence: state is global and process-lifetime only: `sessions[MAX_SESSIONS]`, `port_data[AFE_MAX_PORTS]`, mutex, COPP pointers, COPP bitmap, sample format, and selected route. No route persists across unbind.

Dependencies and integration: depends on q6adm, q6asm/q6afe dt-bindings, ASoC DAPM widgets/routes, and machine drivers exposing FE/BE links. It registers for `qcom,q6adm-routing`.

Risks: the single global pointer is fragile with multiple devices. `q6routing_stream_open()` indexes `sessions[stream_id - 1]`, so invalid stream IDs can corrupt state. Mixer state and hw_params ordering are coupled; opening without a selected port or populated backend format fails. Large macro-expanded route tables are easy to desynchronize from AFE IDs.

Test signals: amixer route toggles update DAPM power, PCM open maps the expected backend, ADM open/matrix-map logs succeed, close frees COPPs, and invalid/unselected routes return errors without leaks.
