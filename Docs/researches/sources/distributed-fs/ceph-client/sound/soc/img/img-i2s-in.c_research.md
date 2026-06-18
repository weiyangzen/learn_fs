# sources/distributed-fs/ceph-client/sound/soc/img/img-i2s-in.c

Purpose: ASoC CPU DAI driver for the Imagination I2S input controller, using dmaengine PCM and runtime/system PM.

Important APIs/types/functions: `struct img_i2s_in` stores MMIO base, sys clock, DMA data, max/active channel pairs, channel register base, DAI driver, and suspend snapshots. DAI ops include trigger, hw_params, set_fmt, and DAI probe. Custom DMA config sets source burst based on channel count.

Control flow: probe maps registers, reads `img,i2s-channels`, computes channel register base, enables runtime PM, initializes/reset hardware, allocates suspend register storage, registers component and dmaengine PCM. `set_fmt()` resumes PM, disables active channels, applies inversion and I2S/left-justified format bits across channels, then restores enables. `hw_params()` validates even channel count and S16/S24/S32 formats, checks sys clock versus bit clock, programs global/channel packing/filter settings, flushes FIFOs, and enables active channels. Trigger toggles the master enable bit.

State and persistence: state tracks `active_channels`, `max_i2s_chan`, DMA FIFO address/width, and register snapshots for system sleep. Runtime PM controls the sys clock. Hardware channel registers persist until reset or suspend/resume restore.

Dependencies/integration: requires platform MMIO resource, `img,i2s-channels`, optional reset `rst`, clock `sys`, dmaengine PCM, and DT compatible `img,i2s-in`.

Risks: channel count must be even and within hardware range; bad DT can move `channel_base` incorrectly. Optional top-level reset fallback relies on manual disable of existing state. `pm_runtime_put()` is used without autosuspend; clock churn may be visible in repeated set_fmt calls. Clock-rate filter thresholds must match hardware tolerances.

Test signals: probe with/without reset, capture for S16/S24/S32 and multiple channel pairs, sys-clock insufficiency rejection, suspend/resume register restore, and dmaengine slave config burst sizing.
