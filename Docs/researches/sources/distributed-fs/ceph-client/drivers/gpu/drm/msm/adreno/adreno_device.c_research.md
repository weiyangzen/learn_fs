# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_device.c

## Purpose

`adreno_device.c` registers the Adreno platform driver, matches device-tree GPU nodes to catalog entries, binds the GPU into the MSM DRM component graph, loads firmware, initializes hardware under runtime PM, and implements system/runtime suspend and resume coordination.

## Important APIs, Types, And Functions

Module parameters are `hang_debug`, `snapshot_debugbus`, `enable_preemption`, `disable_acd`, and `no_gpu`/`skip_gpu`. Public entry points are `adreno_has_gpu()`, `adreno_load_gpu()`, `adreno_register()`, and `adreno_unregister()`. Driver callbacks include `adreno_probe()`, `adreno_remove()`, `adreno_shutdown()`, component `adreno_bind()`/`adreno_unbind()`, PM callbacks, and scheduler suspend/resume helpers. `adreno_info()` searches the family gpulists.

## Control Flow

`find_chipid()` first parses `compatible` strings in `qcom,adreno-XYZ.W`, `amd,imageon-XYZ.W`, or raw hex forms, then falls back to legacy `qcom,chipid`. `adreno_has_gpu()` honors `skip_gpu`, parses the chip ID, and checks that a matching catalog entry exists.

Probe either directly calls `msm_gpu_probe()` for imageon/no-components configurations or adds the device as a DRM component. Bind stores platform config, looks up `adreno_info`, sets private feature flags, calls the generation-specific `info->funcs->init()`, and discovers interconnect paths. `adreno_load_gpu()` loads firmware and optional microcode, enables runtime PM, powers the device, calls `msm_gpu_hw_init()` under `gpu->lock`, drops the autosuspend ref, and initializes debugfs when enabled.

System suspend stops all DRM scheduler workqueues, waits up to one second for `active_submits == 0`, then force-suspends runtime PM; on failure it restarts schedulers. System resume restarts schedulers after force resume. Runtime PM delegates to generation callbacks.

## State And Persistence Behavior

Persistent global/module state is held in module parameters. Per-device state is stored in static `adreno_platform_config config` inside bind, `priv->gpu_pdev`, `config.info`, `config.chip_id`, `priv->is_a2xx`, and `priv->has_cached_coherent`. Runtime PM state is enabled only after firmware is ready, and disabled on hardware-init failure.

## Dependencies And Integration Points

This file links all family catalog lists (`a2xx` through `a8xx`) and delegates real GPU behavior through `adreno_info->funcs`. It integrates with device tree, platform/component framework, DRM scheduler, runtime/system PM, OPP/interconnect lookup, firmware loading, debugfs, and module init/exit from the broader MSM DRM driver.

## Risks

The static `adreno_platform_config config` in `adreno_bind()` is shared storage and assumes one bound Adreno device. Chip-id parsing must remain compatible with old and new DT bindings. Suspend waits only one second for active submits; long-running jobs can block system suspend. `skip_gpu` disables registration globally. Firmware load failures abort GPU load before runtime PM setup, so error ordering matters.

## Test Signals

Signals include correct matching for each DT compatible form, successful bind/unbind, firmware and microcode load, hardware init under runtime PM, debugfs creation, clean runtime suspend with zero active submits, system suspend timeout behavior, and module parameter effects.
