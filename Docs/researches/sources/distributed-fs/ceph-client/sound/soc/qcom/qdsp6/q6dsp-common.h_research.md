# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-common.h

Purpose: `q6dsp-common.h` defines shared PCM channel constants and declares common helper functions for QDSP6 audio drivers.

Important APIs and types: `PCM_MAX_NUM_CHANNEL` is 8. Channel constants define null, front left/right/center, left/right surround, LFE, center surround, left/right back, and top surround positions. Function declarations are `q6dsp_map_channels` and `q6dsp_get_channel_allocation`.

Control flow: callers use constants in media-format structs and call helpers for default channel mapping or HDMI channel allocation.

State and persistence: no state.

Dependencies and integration points: included by `q6asm.h`, `q6dsp-common.c`, APM LPASS DAI code, and any driver that needs shared QDSP6 channel positions.

Risks: constants overlap semantically with similar definitions in `q6apm.h`, creating drift risk. The helper prototype fixes the channel map array to eight entries.

Test signals: compile all includes and verify constants remain aligned with firmware and APM/ASM media-format users.
