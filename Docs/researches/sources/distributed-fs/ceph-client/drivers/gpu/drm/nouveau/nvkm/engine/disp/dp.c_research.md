<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/dp.c

Purpose: generic DisplayPort output implementation: AUX transfers, AUX/eDP power management, link training, LTTPR repeater handling, VBIOS script execution, MST ID helpers, and DP output construction.

Important APIs and functions: `nvkm_dp_new()` creates a DP `nvkm_outp`, resolves the AUX channel from the DCB entry, requires BIOS DP output data, and records whether MST is enabled in the DP table. `nvkm_dp_enable()` switches AUX monitoring and eDP panel power. `nvkm_dp_disable()` runs the DisableLT script. `nvkm_dp_train()` is the public train/retrain callback. Helpers `nvkm_dp_train_link()`, `nvkm_dp_train_cr()`, `nvkm_dp_train_eq()`, `nvkm_dp_train_drive()`, and `nvkm_dp_train_pattern()` implement sink/LTTPR training.

Control flow: training chooses the requested rate, locks `outp->dp.mutex`, populates `ior->dp` state, runs spread and before-training scripts, configures source links through `ior->func->dp->links()`, powers lanes, trains each LTTPR from farthest to sink using clock recovery then channel EQ, clears training pattern, runs after-training script, and unlocks. Retrain skips source reconfiguration and only repeats sink/repeater link training.

State and persistence: updates `outp->dp.enabled`, `aux_pwr`, `aux_pwr_pu`, cached DPCD, link-training target state, and `ior->dp` fields (`mst`, `ef`, `bw`, `nr`). eDP panel power GPIO may be toggled and later restored.

Dependencies and integration points: uses DRM DP register definitions, NVKM AUX/I2C, GPIO, BIOS DP output and init scripts, IOR DP callbacks for hardware-specific drive/pattern/power/link programming, and output acquire/release infrastructure.

Risks: link training is timing-sensitive and sink-dependent. The Ampere IED hack compensates for unchanged VBIOS table versions and must be preserved for newer boards. AUX power management affects laptop panels and can cause resume delays or external-output interference if GPIO restoration is wrong.

Test signals: DP and eDP hotplug, AUX reads/writes, link training at all advertised rates/lane counts, LTTPR repeater chains, MST enablement, suspend/resume, retraining without full modeset, and failure logging on bad sinks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/dp.c -->
