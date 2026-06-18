# sources/distributed-fs/ceph-client/sound/soc/img/img-spdif-in.c

Purpose: ASoC CPU DAI driver for Imagination SPDIF input with dmaengine PCM, IEC958 status controls, configurable lock thresholds, and single/multiple frequency acquisition modes.

Important APIs/types/functions: `struct img_spdif_in` stores MMIO, sys clock, DMA data, lock/tracking settings, frequency configuration, active flag, suspend snapshots, and cached write-only ACLKGEN registers. Helpers calculate clock generator values. DAI controls expose IEC958 status, multi-frequency acquire rates, lock frequency, TRK, and thresholds. DAI ops are trigger, hw_params, and probe.

Control flow: probe maps resources, gets sys clock, resumes PM, resets hardware via reset control or soft reset, initializes spinlock/default lock/TRK values, writes control register, registers component and dmaengine PCM. `hw_params()` accepts stereo S32_LE and programs single-rate clock generation. Mixer controls can program multi-rate clock generators while inactive. Trigger start sets SRT and single/multi SRD mode under lock and marks active; stop clears SRT and active. Suspend saves readable registers and resume rewrites cached write-only aclkgen registers plus snapshots.

State and persistence: lock-protected state includes active/inactive, `multi_freq`, `single_freq`, `multi_freqs`, `trk`, lock thresholds, and cached ACLKGEN values. Runtime PM controls the sys clock. IEC958 status is read from hardware.

Dependencies/integration: requires MMIO, clock `sys`, optional reset `rst`, dmaengine PCM, ALSA kcontrols, and compatible `img,spdif-in`.

Risks: user controls reject changes while active, so user-space must sequence configuration before capture. `img_spdif_in_get_lock_freq()` indexes `multi_freqs` from hardware SAM value minus one without explicit range check; unexpected hardware status could read out of bounds. Lock threshold controls accept signed values but pack into masked fields, so sign extension behavior depends on intended hardware representation. Clock-gen calculation loops until hold >= 120 and assumes valid sys clock/rate ratios.

Test signals: capture at supported rates, single vs multi acquire controls, IEC958 status reads, lock/unlock frequency reporting, suspend/resume restoring write-only registers, EBUSY behavior for active control changes, and fuzz tests for SAM status values if hardware can expose invalid encodings.
