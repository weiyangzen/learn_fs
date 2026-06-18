# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-pcm.c

Purpose: implements two MT8183 PCM DAIs for modem/Bluetooth-style PCM links, including DAPM routes between DL/ADDA sources and modem pins plus register programming for PCM interface modes.

Important APIs/types/functions: enums describe PCM bit clock, sync, modem, AFIFO, clock-source, word-length, mode, format, inversion, and enable fields; DAPM mixers route DL2/DL1/ADDA UL into PCM playback channels; widgets include `PCM_1_EN`, `PCM_2_EN`, modem input/output pins; routes connect `AFE_TO_MD*` and `MD*_TO_AFE`; `mtk_dai_pcm_hw_params` programs `PCM_INTF_CON1` or `PCM2_INTF_CON`; DAI drivers expose `PCM 1` and `PCM 2` playback/capture with symmetric rate/sample bits.

Control flow: register callback contributes PCM DAIs, widgets, and routes to the AFE. hw_params maps the requested rate to a hardware mode. If either playback or capture widget for the DAI is already active, it returns without reprogramming shared registers. Otherwise it constructs the PCM register value for PCM mode B, AFIFO, dual-mic TX, and per-interface mode fields, then writes the appropriate register.

State and persistence: no private state is allocated. PCM interface state persists in AFE registers and is gated by DAPM supplies. Active widget state prevents reconfiguration while the paired direction is running.

Dependencies and integration: depends on MT8183 rate transform helper, register definitions, interconnection indices, and DAPM endpoint names from memif/ADDA/hostless machine routes.

Risks: active-widget checks avoid midstream reconfiguration but can also leave a second stream with mismatched requested params if constraints fail to enforce symmetry. Only rates 8/16/32/48 kHz are advertised. PCM mode and modem selection are hardcoded for internal modem, slave mode, PCM mode B.

Test signals: PCM1/PCM2 playback and capture at all four rates, simultaneous duplex startup order, DAPM modem pin routing, register trace for `PCM_INTF_CON1`/`PCM2_INTF_CON`, and suspend/resume preserving cached settings.
