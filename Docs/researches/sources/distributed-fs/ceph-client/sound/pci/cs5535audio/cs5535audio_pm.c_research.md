# sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio_pm.c

Purpose: sleep power-management support for CS5535/CS5536 audio.

Important APIs and types: `snd_cs5535audio_stop_hardware` asserts AC-link shutdown. `snd_cs5535audio_suspend` changes ALSA power state, suspends AC97, saves active DMA PRD registers, and shuts down the link. `snd_cs5535audio_resume` warm-resets the AC link, waits for `PRM_RDY_STS`, re-prepares active substreams, restores PRD registers, resumes AC97, and returns ALSA power state to D0. `SIMPLE_DEV_PM_OPS` exports `snd_cs5535audio_pm`.

Control flow: suspend iterates both playback/capture DMA slots and saves PRD only when `substream` is non-null. Resume writes `ACC_CODEC_CNTL_LNK_WRM_RST`, polls codec status for up to 50 micro-delay iterations, then calls each active substream's `prepare` callback before restoring the saved PRD address.

State and persistence: only volatile resume state is `cs5535audio_dma.saved_prd`; codec state is delegated to AC97 suspend/resume.

Dependencies and integration: compiled under `CONFIG_PM_SLEEP` and referenced by the PCI driver's `.pm` pointer. Depends on ALSA power and AC97 PM helpers.

Risks and test signals: resume logs but continues after AC-link-ready timeout; active streams are prepared but not restarted, leaving trigger to ALSA. Test suspend/resume with idle, playback-only, capture-only, and duplex streams; verify PRD registers and AC97 rates are restored.
