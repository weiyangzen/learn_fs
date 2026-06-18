# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_drv.c

## Purpose

`tidss_drv.c` is the platform DRM driver entry point for TI Keystone/TIDSS display controllers. It owns DRM device allocation, runtime/system PM plumbing, DISPC and OLDI initialization, modeset setup, IRQ installation, device registration, fbdev/client setup, and platform remove/shutdown ordering.

## Important APIs, Types, and Functions

- `tidss_runtime_get()` and `tidss_runtime_put()` wrap runtime PM resume/autosuspend for atomic commit paths.
- Runtime PM callbacks delegate to `dispc_runtime_suspend()` and `dispc_runtime_resume()`.
- System suspend/resume callbacks call `drm_mode_config_helper_suspend()` and `drm_mode_config_helper_resume()`.
- `tidss_driver` defines DRM features, DMA GEM/fbdev helper ops, file ops, release callback, and driver identity.
- `tidss_probe()` performs all platform initialization.
- `tidss_remove()` unregisters the DRM device, shuts down atomic state, removes IRQs, disables PM, deinitializes OLDI, and clears the DISPC pointer.
- `tidss_of_table` maps compatible strings to the `dispc_features` tables exported by `tidss_dispc.c`.

## Control Flow

Probe allocates `struct tidss_device` embedded around `struct drm_device`, stores the OF-matched feature table, sets platform drvdata, initializes the IRQ spinlock, initializes DISPC, initializes OLDI bridges, enables runtime PM with autosuspend, sets up modesetting, retrieves and installs the platform IRQ, initializes poll helpers, resets mode config, registers the DRM device, removes conflicting firmware/simple framebuffers, and starts DRM client setup. Error paths unwind IRQs, runtime PM, and OLDI state.

Remove unregisters first to prevent new users, then calls `drm_atomic_helper_shutdown()`, uninstalls IRQs, handles no-PM suspend fallback, disables autosuspend/runtime PM, deinitializes OLDI bridges, and marks the devm-managed DISPC pointer NULL. Shutdown only performs atomic shutdown.

## State and Persistence Behavior

`struct tidss_device` persists as the DRM private object. Runtime PM state is active during commits and autosuspended otherwise. `tidss_release()` finalizes polling, while most allocations are devm/drmm managed. `tidss->feat`, `tidss->dispc`, CRTC/plane arrays, OLDI array, IRQ number, IRQ mask, and external VP clock flags are shared across submodules.

## Dependencies and Integration Points

The file depends on DRM managed allocation, DMA GEM helpers, fbdev DMA helpers, DRM client setup, aperture conflict removal, platform OF matching, runtime PM, and module platform-driver helpers. It integrates directly with `tidss_dispc`, `tidss_oldi`, `tidss_kms`, and `tidss_irq`.

## Risks and Edge Cases

- `tidss_runtime_get()` warns on failure but still returns the PM error; callers must not ignore fatal PM failures in contexts where hardware access follows.
- `aperture_remove_all_conflicting_devices()` happens after `drm_dev_register()`, so a failure unregisters the DRM device but userspace may briefly observe it.
- Under `!CONFIG_PM`, manual DISPC resume/suspend paths must mirror runtime PM behavior.
- Probe error unwinding relies on devm/drmm for many resources; ordering mistakes can leave hardware enabled until device release.
- `tidss_shutdown()` passes platform drvdata to `drm_atomic_helper_shutdown()`, which is valid only because drvdata is a `struct tidss_device` embedding `struct drm_device` first? In this file `struct drm_device` is the first member, so the cast works through layout assumptions.

## Test Signals

Test probe and remove on every compatible, deferred panel/bridge probing, IRQ-not-found paths, runtime PM autosuspend while idle, suspend/resume with active scanout, fbdev takeover from firmware framebuffer, and no-PM kernel configurations. KASAN/lockdep should cover remove/shutdown ordering and PM usage during atomic commits.
