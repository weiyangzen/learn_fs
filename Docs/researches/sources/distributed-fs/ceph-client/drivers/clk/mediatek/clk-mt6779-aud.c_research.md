<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-aud.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-aud.c

### Purpose
This driver registers MT6779 audio subsystem gates across two audio gate banks.

### Important APIs, Types, And Functions
It defines `audio0_cg_regs`, `audio1_cg_regs`, `GATE_AUDIO0/1`, `audio_clks[]`, `audio_desc`, and a simple platform driver matching `mediatek,mt6779-audio`.

### Control Flow, State, And Persistence
Simple probe registers the audio gate provider. Gate state persists in audio subsystem registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on audio CCF consumers and MT6779 clock bindings. Risks include parent mismatch with the main MT6779 top driver and disabling always-needed audio interface clocks. Test signals include ALSA probe/playback/capture and `clk_summary` enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-aud.c -->
