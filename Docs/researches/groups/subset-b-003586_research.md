# Research Report: subset-b-003586

This grouped report covers the i915 display files assigned to `subset-b-003586`. Each file section preserves the original source path and is wrapped with the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display.h

## Purpose
`intel_display.h` is the broad public display header for the i915 display subsystem. It provides stable naming helpers, display topology iteration macros, atomic state iteration wrappers, and declarations for modeset, pipe, plane, transcoder, encoder, M/N timing, power-domain, and state-checking functions implemented elsewhere. It is not an implementation file; its main persistence effect is the contract it imposes on enum values, list ownership, and state traversal patterns used throughout the display stack.

## Important APIs, Types, And Functions
The file defines `pipe_name()`, `transcoder_name()`, `transcoder_is_dsi()`, `plane_name()`, `port_identifier()`, `port_name()`, and `phy_name()` for consistent diagnostics. It introduces `enum tc_port`, `enum phy`, and `enum phy_fia`, building on display limits. The numerous `for_each_*` macros are central APIs: they walk pipes, ports, PHYs, DBUF slices, CRTCs, planes, encoders, DP encoders, connectors, and old/new DRM atomic state entries. The declaration set exposes `intel_atomic_check()`, `intel_atomic_commit()`, `intel_mode_valid()`, pipe config read/compare, joiner helpers, transcoder enable/disable, M/N register helpers, encoder/PHY mapping, FIFO underrun arming, pipe bpp limits, modeset power-domain acquisition/release, initial commit, and assertions.

## Control Flow And State
Control flow is macro-driven. Iterators combine DRM lists, i915 `display->pipe_list`, runtime masks from `DISPLAY_RUNTIME_INFO()`, and atomic state arrays. Joiner and modeset order macros deliberately walk primary and secondary pipe masks in different directions for disable and enable sequencing. The header assumes pipe and transcoder numbering from `intel_display_limits.h`, and many macros depend on `struct intel_display` runtime masks being initialized before use. `INTEL_DISPLAY_STATE_WARN()` converts display state mismatches into either `drm_WARN()` or `drm_err()` based on the `verbose_state_checks` parameter.

## Dependencies And Integration Points
This header integrates DRM atomic/mode APIs with i915 display objects from `intel_display_types.h`, runtime device info from `intel_display_device.h`, and register abstractions through `i915_reg_defs.h`. It is included by low-level modeset, plane, encoder, connector, and IRQ code that needs shared topology traversal. `to_intel_display(dev)` and list layout are expected to be valid for all iterator users.

## Risks And Test Signals
The main risks are macro side effects, stale runtime masks, and assumptions that pipe/transcoder enum values remain stable. Bugs show up as missed modesets, wrong pipe order for joiner modes, invalid state comparisons, or warnings from `INTEL_DISPLAY_STATE_WARN()`. Useful tests include DRM atomic KMS tests, joiner/bigjoiner/ultrajoiner modes, pipe-fused platforms, MST/DP encoder enumeration, and state-checker logs during boot, suspend/resume, and fastset commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_conversion.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_conversion.c

## Purpose
`intel_display_conversion.c` implements the transitional helper that maps a DRM core device pointer to the display subsystem root object. It exists to support the split between i915 and xe style parent devices while display code is being converted toward `struct intel_display`.

## Important APIs, Types, And Functions
The only exported function is `__drm_to_display(struct drm_device *drm)`. It uses `container_of()` to treat the DRM device as part of `struct __intel_generic_device`, then returns that generic wrapper's `display` pointer. The helper relies on `<drm/intel/display_member.h>`, which defines the generic layout and static assertions for the shared `drm_device` and `intel_display *` member offsets.

## Control Flow And State
There is no branching or mutable state. The function is a pure pointer conversion with a strong layout invariant: both `struct drm_i915_private` and `struct xe_device` must embed compatible members at the same relative offsets. If that invariant is broken, the function returns an invalid pointer and all display callers using DRM-to-display conversion become unsafe.

## Dependencies And Integration Points
The helper is declared in `intel_display_conversion.h` and is consumed by code paths that need to obtain `struct intel_display` from DRM objects before direct display ownership has been threaded through. It is part of the display-member compatibility layer shared by i915 and xe.

## Risks And Test Signals
The risk is structural rather than algorithmic: offset drift in parent device structs would create silent memory corruption. The comment points to `INTEL_DISPLAY_MEMBER_STATIC_ASSERT()` as the compile-time guard. Build coverage across both i915 and xe configurations is the main signal. Runtime failures would appear very early as crashes in display init, debugfs, or atomic paths that call `to_intel_display()`/conversion helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_conversion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_conversion.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_conversion.h

## Purpose
`intel_display_conversion.h` declares transitional DRM-to-display conversion helpers. It intentionally stays small because it bridges two ownership models rather than defining permanent display policy.

## Important APIs, Types, And Functions
The header forward declares `struct drm_device` and `struct intel_display`, then declares `struct intel_display *__drm_to_display(struct drm_device *drm)`. Include guards prevent duplicate declarations. No inline logic, macros, or state definitions live here.

## Control Flow And State
There is no control flow or persistent state in the header. Its behavioral contract is delegated to `intel_display_conversion.c`: callers passing a valid DRM device associated with an i915/xe generic display parent receive the associated `intel_display`.

## Dependencies And Integration Points
The header is used by display code that cannot yet include heavier internal structures or that needs a neutral conversion API during display-core migration. Its minimal forward declarations reduce include coupling and make it suitable for broad inclusion.

## Risks And Test Signals
Risk is mainly API misuse: calling the helper for a DRM device that does not satisfy the shared layout contract is invalid. Build tests catch declaration mismatches; runtime KMS probe and debugfs access catch bad conversions. Long term, this file should shrink or disappear as direct `struct intel_display *` plumbing replaces conversion calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_conversion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_core.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_core.h

## Purpose
`intel_display_core.h` defines the central `struct intel_display` aggregate and major display subsystem state containers. It is the display driver's in-memory root: platform identification, parent callbacks, hooks, global modeset objects, locks, cached hardware state, power domains, workqueues, VBT data, hotplug state, IRQ masks, watermarks, audio, DPLL, FBC, GMBUS, HDCP, DMC, and restore state all hang from this structure.

## Important APIs, Types, And Functions
Important types include `struct intel_display_funcs`, `struct intel_wm_funcs`, `struct intel_audio_state`, `struct intel_audio`, `struct intel_dpll_global`, `struct intel_frontbuffer_tracking`, `struct intel_hotplug`, `struct intel_vbt_data`, `struct intel_wm`, and `struct intel_display`. The function-pointer tables select platform-specific CRTC enable/disable/readout, watermark, CDCLK, DPLL, hotplug, FDI, color, and audio behavior. Several constants define hardware table sizes such as `I915_NUM_QGV_POINTS` and `I915_NUM_PSF_GV_POINTS`.

## Control Flow And State
This header does not implement control flow, but it encodes synchronization and persistence rules. `display->irq.lock` protects interrupt masks and HPD work enablement; `fb_tracking.lock` protects frontbuffer busy bits; `wm.wm_mutex` protects watermark programming and active watermark state; `dpll.lock` serializes shared PLL programming; mutexes protect GMBUS, HDCP, backlight, PPS, SBI, PM demand, and FBC system-cache state. Restore fields persist suspend/reset modeset state and register shadows. Workqueues split ordered modesets, high-priority flips, cleanup, and unordered display work.

## Dependencies And Integration Points
The structure integrates many display modules: CDCLK, DPLL, FBC, global state, GMBUS, opregion, PCH, power domains, DMC wakelocks, watermark types, DRM connector/modeset locks, and platform info from `intel_display_device.h`. Almost every display implementation file either receives `struct intel_display *` directly or obtains it from a child object.

## Risks And Test Signals
Risks concentrate around lock ordering, lifetime ownership, stale cached hardware state, and teardown ordering of workqueues versus objects they reference. State regressions show up as suspend/resume failures, hotplug storms, watermark corruption, missed vblank/flip events, HDCP/audio races, and use-after-free during driver unload. Test signals include lockdep, KMS suspend/resume, hotplug and MST stress, PSR/FBC tests, runtime PM assertions, debugfs dumps of display info, and CI coverage across old GMCH, PCH-split, and Xe display generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs.c

## Purpose
`intel_display_debugfs.c` exposes i915 display diagnostics and selected test controls through debugfs. It provides global display capability/state dumps, framebuffer and power-domain views, CRTC/plane/connector descriptions, DPLL and DDB reports, LPSP and MST status, FIFO underrun rearming, connector DSC/FEC overrides, forced joined-pipe controls, and per-CRTC current bpc/pipe files.

## Important APIs, Types, And Functions
Public entry points are `intel_display_debugfs_register()`, `intel_connector_debugfs_add()`, and `intel_crtc_debugfs_add()`. Global show functions include `intel_display_caps()`, `i915_frontbuffer_tracking()`, `i915_sr_status()`, `i915_gem_framebuffer_info()`, `i915_power_domain_info()`, `i915_display_info()`, `i915_shared_dplls_info()`, `i915_ddb_info()`, `i915_lpsp_status()`, and `i915_dp_mst_info()`. Connector controls include `i915_dsc_fec_support`, `i915_dsc_bpc`, `i915_dsc_output_format`, `i915_dsc_fractional_bpp`, `i915_joiner_force_enable`, and `i915_lpsp_capability`. CRTC controls include optional vblank-evasion stats, `i915_current_bpc`, and `i915_pipe`.

## Control Flow And State
Most functions are seq-file show paths that obtain `struct intel_display` from the DRM info node and then lock only the state they inspect. Global display info takes a runtime PM reference and locks all modeset objects while walking CRTCs and connectors. Framebuffer info locks `mode_config.fb_lock`. DPLL and DDB dumps lock modeset state. Writable debugfs files mutate test-only state: DSC force flags in `struct intel_dp`, `connector->force_joined_pipes`, FIFO underrun reporting state, and vblank debug counters. Several writes parse user input through `kstrtobool_from_user()` or `kstrtoint_from_user()`.

## Dependencies And Integration Points
The file integrates DRM debugfs helpers, seq files, connector iteration, DP/MST helpers, HDCP, PSR, FBC, WM, DMC, HPD, GMBUS, PPS, ALPM, link training, link bandwidth, TC, and display power helpers. `intel_display_debugfs_register()` composes global display debugfs setup by delegating to many submodules and then registering display params through `intel_display_debugfs_params()`.

## Risks And Test Signals
Risks include exposing mutable hardware-forcing knobs that are not validated like normal UAPI, lock ordering in show paths, stale connector state if hotplug races with debugfs reads, and writable controls affecting subsequent modesets without explicit rollback. The file correctly ignores debugfs creation failures and returns `-ENODEV` for disconnected or unsupported objects. Test signals include debugfs smoke reads under connected/disconnected states, DSC forced-mode KMS tests, underrun rearm behavior, lockdep with concurrent hotplug/modeset/debugfs access, and CI comparison of `i915_display_info`/DDB/DPLL dumps before and after modesets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs.h

## Purpose
`intel_display_debugfs.h` declares the display debugfs registration hooks and provides no-op stubs when `CONFIG_DEBUG_FS` is disabled. It keeps debugfs integration optional without forcing callers to add preprocessor guards.

## Important APIs, Types, And Functions
The header forward declares `struct intel_connector`, `struct intel_crtc`, and `struct intel_display`. With debugfs enabled it declares `intel_display_debugfs_register()`, `intel_connector_debugfs_add()`, and `intel_crtc_debugfs_add()`. With debugfs disabled, it defines static inline empty versions of the same functions.

## Control Flow And State
There is no runtime state in this header. Control flow is compile-time selection based on `CONFIG_DEBUG_FS`. Callers can invoke the hooks unconditionally, and either real debugfs files are created or calls compile away.

## Dependencies And Integration Points
The header is included by display driver registration, connector registration, and CRTC registration paths. It is the boundary between the core display lifecycle and debugfs implementation in `intel_display_debugfs.c`.

## Risks And Test Signals
The primary risk is interface drift between enabled declarations and disabled stubs. Build testing with `CONFIG_DEBUG_FS=y` and `CONFIG_DEBUG_FS=n` catches this. Runtime test signals are the presence or absence of expected debugfs files and successful display init when debugfs support is compiled out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs_params.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs_params.c

## Purpose
`intel_display_debugfs_params.c` creates a debugfs directory exposing display module parameters for inspection and, when permitted by mode bits, mutation. It provides typed file operations for display params that are not handled by generic debugfs helpers.

## Important APIs, Types, And Functions
The public API is `intel_display_debugfs_params(struct intel_display *display)`. Internal helpers implement integer and unsigned-integer seq-file show/open/write paths: `intel_display_param_int_show/open/write()` and `intel_display_param_uint_show/open/write()`. `intel_display_debugfs_create_int()` and `intel_display_debugfs_create_uint()` select read-only or read-write file operations based on mode. `_intel_display_param_create_file()` uses C11 `_Generic` to dispatch `bool *`, `int *`, `unsigned int *`, `unsigned long *`, and `char **` values to the right debugfs creation routine.

## Control Flow And State
The function builds a directory named `<driver_name>_params` under the DRM debugfs root, reusing it if it already exists. It iterates `INTEL_DISPLAY_PARAMS_FOR_EACH(REGISTER)` and creates a file for each parameter with a nonzero mode. Writes parse integers or unsigned integers first and fall back to boolean parsing, allowing common boolean values for numeric toggles. The persistent state is `display->params`; debugfs writes mutate that in-memory parameter struct and affect subsequent display logic that consults those params.

## Dependencies And Integration Points
This file depends on `intel_display_params.h` for the parameter list and metadata, `intel_display_core.h` for `display->params`, and Linux debugfs/seq-file helpers. It is called by global display debugfs registration after other display debugfs files are created.

## Risks And Test Signals
Risks include unsafe debugfs lifetime if files outlive `display`, unvalidated parameter changes that affect active hardware paths, and type mismatches in the `_Generic` dispatch if a new parameter type is added. The use of `debugfs_create_file_unsafe()` is acceptable only because debugfs lifetime is tied to driver/device teardown. Test signals include reading every param file, writing allowed params, confirming read-only modes reject writes, checking boolean fallback for numeric params, and building after adding new parameter types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs_params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs_params.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs_params.h

## Purpose
`intel_display_debugfs_params.h` declares the display-parameter debugfs registration function. It is a narrow interface used by the broader display debugfs setup code.

## Important APIs, Types, And Functions
The header forward declares `struct intel_display` and declares `void intel_display_debugfs_params(struct intel_display *display)`. It has no stubs, because the implementation file itself is part of the debugfs build path that includes it.

## Control Flow And State
No state or control flow is defined here. The declared function creates debugfs files for `display->params` when invoked.

## Dependencies And Integration Points
The header is consumed by `intel_display_debugfs.c`. It intentionally avoids including `intel_display_core.h`, reducing include dependencies for callers that only need the declaration.

## Risks And Test Signals
Risk is limited to declaration/definition drift. Build coverage and debugfs file creation smoke tests are sufficient. Behavioral risks are in the `.c` implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_device.c

## Purpose
`intel_display_device.c` maps PCI devices and display IP versions to i915 display capabilities, platform flags, subplatform flags, stepping information, static device info, and runtime display masks. It is the display capability database and probe-time detector for legacy PCI-ID platforms and newer GMD-ID based platforms.

## Important APIs, Types, And Functions
Public APIs are `intel_display_device_probe()`, `intel_display_device_remove()`, `intel_display_device_info_runtime_init()`, `intel_display_device_info_print()`, `intel_display_device_present()`, and `intel_display_device_enabled()`. Internal descriptors include `struct platform_desc`, `struct subplatform_desc`, and `struct stepping_desc`. The file defines many `intel_display_device_info` instances and macros for pipe/transcoder/cursor register offsets, color LUT capabilities, DBUF sizes, feature flags, runtime defaults, FBC masks, and port masks. `probe_gmdid_display()` reads `GMD_ID_DISPLAY` from MMIO for GMD-ID devices. `get_pre_gmdid_step()` maps PCI revision IDs to symbolic display steppings.

## Control Flow And State
Probe allocates `struct intel_display`, stores the DRM backpointer and parent interface, copies display params, rejects known no-display SKUs, finds the platform descriptor by PCI ID, optionally probes GMD ID, copies static runtime defaults, merges subplatform flags, initializes stepping, and logs the detected display version. Runtime init then mutates `DISPLAY_RUNTIME_INFO()` based on fuses, workarounds, platform restrictions, scaler/sprite counts, pipe disables, HDCP/DMC/DSC disable straps, DBUF overlap capability, eDP-on-TypeC support, and rawclk readout. If display is absent or fused off, runtime info is zeroed and DRM modeset/atomic features are disabled.

## Dependencies And Integration Points
The file depends on PCI ID macros, display register definitions, `intel_de` MMIO access, display power, opregion headless detection, display workarounds, FBC IDs, color management constants, and display params. Its outputs drive almost every `HAS_*`, `DISPLAY_VER*`, port, pipe, transcoder, scaler, sprite, and feature check used by modeset, IRQ, debugfs, power, PSR, FBC, and watermark code.

## Risks And Test Signals
The largest risk is incorrect platform data: wrong masks or offsets cause missing connectors, invalid register programming, disabled features, or use of fused-off resources. GMD-ID probing can fail if MMIO mapping fails or an unknown display release is encountered, disabling display. Step-map gaps deliberately choose a later or future step, which may affect workaround selection. Test signals include boot logs with detected display version/stepping, `intel_display_caps`, connector enumeration, pipe-fused SKU tests, GMD-ID platform bring-up, rawclk sanity, and KMS coverage across old GMCH through Xe2/Xe3 platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_device.h

## Purpose
`intel_display_device.h` defines display platform flags, static and runtime display capability structures, feature query macros, display-version helpers, register-offset helpers, and the public display-device probe/runtime API. It is the main interface for asking what display hardware exists and which capabilities are enabled.

## Important APIs, Types, And Functions
The `INTEL_DISPLAY_PLATFORMS()` macro enumerates platform and subplatform bits used in `struct intel_display_platforms`. `DEV_INFO_DISPLAY_FOR_EACH_FLAG()` defines static feature flags in `struct intel_display_device_info`. The header defines many feature macros such as `HAS_DISPLAY`, `HAS_DDI`, `HAS_DSC`, `HAS_DMC`, `HAS_FBC`, `HAS_PSR`, `HAS_DP_MST`, `HAS_HOTPLUG`, `HAS_GMCH`, `HAS_TRANSCODER`, `HAS_ULTRAJOINER`, and version/step helpers like `DISPLAY_VER()`, `DISPLAY_VERx100()`, `IS_DISPLAY_VER()`, and `IS_DISPLAY_STEP()`. `struct intel_display_runtime_info` carries mutable runtime masks and capabilities; `struct intel_display_device_info` carries static defaults, flags, offsets, DBUF info, and color LUT limits.

## Control Flow And State
The header itself has no runtime flow, but it defines the accessor model: `DISPLAY_INFO(display)` points to immutable static capability data, while `DISPLAY_RUNTIME_INFO(display)` points to mutable runtime data initialized from defaults and then adjusted by fuses/workarounds. Register-offset macros derive pipe/transcoder/cursor MMIO offsets from static arrays plus `DISPLAY_MMIO_BASE()`.

## Dependencies And Integration Points
It depends on `intel_display_limits.h` for stable enum sizes and pipe/port definitions. The APIs are implemented in `intel_display_device.c` and consumed by display driver probe, modeset, IRQ, power, debugfs, and feature-specific modules. The macros encode many policy decisions that downstream code treats as authoritative.

## Risks And Test Signals
Risks include stale feature predicates, mismatched static/runtime capability use, bitfield-size overflows as platform counts grow, and incorrect display-version comparisons for GMD-ID releases. Tests should include allmodconfig/build coverage, platform-specific KMS boot tests, debugfs capability dumps, feature-specific tests for PSR/DSC/FBC/MST/VRR/joiners, and stepping/workaround validation on affected SKUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_driver.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_driver.c

## Purpose
`intel_display_driver.c` provides high-level display lifecycle entry points between the parent i915/xe driver and lower-level display modules. It sequences probe, registration, user access gating, suspend/resume, and removal without embedding detailed per-platform programming.

## Important APIs, Types, And Functions
Public functions include `intel_display_driver_probe_defer()`, `intel_display_driver_init_hw()`, `intel_display_driver_early_probe()`, `intel_display_driver_probe_noirq()`, `intel_display_driver_probe_nogem()`, `intel_display_driver_probe()`, `intel_display_driver_register()`, remove/unregister variants, suspend/resume functions, and display access controls. Static helpers define DRM mode config callbacks (`intel_mode_funcs`, `intel_mode_config_funcs`), initialize/cleanup mode config, set plane possible CRTCs, and set/check access state.

## Control Flow And State
Probe is split into ordered phases. Early probe detects PCH, initializes locks and hooks. `probe_noirq()` initializes vblank, BIOS, PSR workarounds, power domains, PM demand, workqueues, DMC, mode config, CDCLK, color, DBUF, bandwidth, quirks, and FBC. `probe_nogem()` initializes WM, panel SSC, PPS, GMBUS, CRTCs, DPLLs, hardware state, outputs, DP tunnel manager, disables user access, reads current modeset state, and sanitizes watermarks. `probe()` runs post-GEM work: HDCP component, flip queue, initial commit, overlay, HPD, and IPC watermarks. Registration enables VGA/opregion/ACPI/audio/debugfs/fbdev and user access. Teardown and unregister reverse these layers and flush workqueues.

## Dependencies And Integration Points
The file orchestrates nearly every display submodule: BIOS/VBT, power domains, DMC, PM demand, CRTC/plane, CDCLK, color, DBUF, BW, DPLL, FDI, outputs, DP tunnel/MST, HDCP, flipq, overlay, HPD, watermark, VGA, opregion, ACPI, audio, fbdev, and debugfs. DRM atomic helper callbacks bind i915 display operations into the DRM core.

## Risks And Test Signals
Risks are ordering bugs, partial-probe cleanup leaks, workqueue lifetime races, and user access opening before hardware state is safe. Access gating is important during load/unload/suspend to prevent user modesets and connector probes from touching hardware at unsafe times. Test signals include probe error injection, boot on no-display and fused-off devices, suspend/resume/hibernate, driver unload/reload, MST suspend/resume, hotplug after fbdev setup, lockdep during access transitions, and initial commit failures logged without breaking driver load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_driver.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_driver.h

## Purpose
`intel_display_driver.h` declares the high-level display driver lifecycle and access-control API. It is the parent-driver facing contract for initializing, registering, suspending, resuming, and removing display support.

## Important APIs, Types, And Functions
The header declares probe phases (`probe_defer`, `init_hw`, `early_probe`, `probe_noirq`, `probe_nogem`, `probe`), registration/removal phases (`register`, `unregister`, `remove`, `remove_noirq`, `remove_nogem`), suspend/resume (`intel_display_driver_suspend()`, `intel_display_driver_resume()`, `__intel_display_driver_resume()`), and access controls (`enable_user_access`, `disable_user_access`, `suspend_access`, `resume_access`, `check_access`). It forward declares DRM atomic and modeset acquire state objects, `struct intel_display`, and `struct pci_dev`.

## Control Flow And State
The header encodes the lifecycle split used by the parent driver. The noirq/nogem/probe naming matters: callers must invoke phases in the correct order relative to IRQ install and GEM initialization, and remove phases must be paired with the corresponding successful probe phases. Access-control calls mutate `display->access` in the implementation.

## Dependencies And Integration Points
This file is included by parent driver code and reset code. The special `__intel_display_driver_resume()` declaration is explicitly an interface for display reset paths that need to restore duplicated atomic state with an existing modeset acquire context.

## Risks And Test Signals
Risks are primarily call-order mistakes and mismatched cleanup after partial failures. Build tests catch signature drift; runtime tests should exercise full probe/remove, no-display devices, suspend/resume, display reset, and user-access rejection paths during suspend/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_irq.c

## Purpose
`intel_display_irq.c` implements display interrupt reset, postinstall, mask updates, acknowledgment, handling, vblank enable/disable, power-well IRQ reinitialization, fault reporting, and lightweight IRQ snapshot capture for i915 display generations from legacy i8xx/i9xx through gen11+ and Xe display IP.

## Important APIs, Types, And Functions
Public functions include mask updaters (`ilk_update_display_irq()`, `bdw_update_port_irq()`, `bdw_enable/disable_pipe_irq()`, `ibx_display_interrupt_update()`), vblank controls (`i8xx`, `i915gm`, `i965`, `ilk`, `bdw` variants), IRQ handlers (`ilk_display_irq_handler()`, `gen8_de_irq_handler()`, `gen11_display_irq_handler()`, GU misc handlers), reset/postinstall routines for i9xx/ilk/vlv/gen8/gen11/dg1, VLV display IRQ runtime enable/disable, pipestat helpers, power-well hooks, and `intel_display_irq_snapshot_capture/print()`. Internal helpers handle IIR zero assertions, pipe faults, CRC delivery, flip-done events, PCH IRQs, GTT/page-table faults, PSR, AUX, HPD, GMBUS, DSB, PM demand, DSI TE, and underruns.

## Control Flow And State
Interrupt setup masks everything, clears queued IIR/EIR bits, then postinstall enables generation-specific sources. Runtime updates are serialized by `display->irq.lock` and often assert that the parent IRQ is enabled. Cached masks in `display->irq` avoid unsafe reads or preserve state across power domains. Handlers ack IIR bits before dispatch, then route to subhandlers based on generation and source group. Vblank enabling toggles pipestat or DE pipe bits, handles PSR frame-counter restore, and notifies PSR when BDW+ vblank enable count transitions.

## Dependencies And Integration Points
The file integrates display MMIO access (`intel_de`), DRM vblank/event delivery, HPD IRQ helpers, AUX, GMBUS, opregion ASLE, PSR, DMC/PipeDMC, DSB, FIFO underrun, plane fault capture, PCH handlers, parent IRQ state, runtime PM assertions, and pipe CRC debugfs support. Its generation-specific branches rely heavily on `DISPLAY_VER()`, platform flags, PCH type, and runtime pipe/transcoder masks.

## Risks And Test Signals
Risks include lost interrupts due to wrong ack order, stale cached masks, accessing powered-down pipe/transcoder registers, missed PCH/PICA forwarding, lock misuse in interrupt context, incorrect fault-bit-to-plane mapping, and vblank/PSR interactions causing stuck frame counters. Test signals include DRM vblank tests, page-flip completion, hotplug/AUX storm testing, pipe CRC capture, FIFO underrun injection, suspend/runtime-PM power-well cycling, fault reporting logs, PICA/PCH IRQ tests on newer platforms, lockdep, and IRQ reset/postinstall behavior during driver load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_irq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_irq.h

## Purpose
`intel_display_irq.h` declares the display interrupt API used by platform IRQ installation, vblank support, power-well management, hotplug/AUX handlers, and error reporting. It abstracts generation-specific display IRQ details behind common names.

## Important APIs, Types, And Functions
The header declares IRQ update helpers for ILK/PCH/BDW, VLV display IRQ runtime toggles, vblank enable/disable variants, master disable/enable for ILK-style display IRQs, top-level handlers for ILK/gen8/gen11/GU misc, reset and postinstall functions for major generations, pipestat helpers, VLV error ack/handler, IRQ initialization, i915gm C-state workaround toggling, PICA AUX mask helper, and IRQ snapshot capture/print. It forward declares `struct drm_crtc`, `struct drm_printer`, `struct intel_display`, and `struct intel_display_irq_snapshot`.

## Control Flow And State
The header does not implement logic, but it defines call points that the parent interrupt code must sequence: reset before install/uninstall, postinstall after core IRQ setup, handler calls from master IRQ dispatch, and vblank callbacks from DRM CRTC funcs. Snapshot allocation/capture is separated from printing to support error-state reporting.

## Dependencies And Integration Points
It includes `intel_display_limits.h` for `enum pipe` and pipe array sizes. It is consumed by display driver probe, parent IRQ code, power management, vblank setup, and error-state code. Implementations rely on `display->irq` state from `intel_display_core.h`.

## Risks And Test Signals
Risks come from mismatched generation selection by callers, especially selecting the wrong vblank or postinstall hooks for a platform. Build coverage catches signature drift; runtime signals include working vblank counters, hotplug/AUX interrupts, no spurious master IRQ logs, and successful error-state IRQ snapshot printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_jiffies.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_jiffies.h

## Purpose
`intel_display_jiffies.h` provides small timeout helpers for display code that needs millisecond-based waits expressed in jiffies while avoiding zero-timeout truncation and accounting for elapsed time between two events.

## Important APIs, Types, And Functions
`msecs_to_jiffies_timeout(unsigned int m)` converts milliseconds to jiffies and adds one tick, capped at `MAX_JIFFY_OFFSET`. `wait_remaining_ms_from_jiffies(unsigned long timestamp_jiffies, int to_wait_ms)` waits only the remaining time until `timestamp_jiffies + timeout`, using `schedule_timeout_uninterruptible()` in a loop.

## Control Flow And State
The helpers are inline and stateless. `wait_remaining_ms_from_jiffies()` snapshots `jiffies` once into `tmp_jiffies`, computes a target, and sleeps only if the target is after the snapshot. It repeatedly schedules until the timeout remainder reaches zero. The design avoids re-reading `jiffies` during arithmetic and avoids sleeping if the intended interval already elapsed.

## Dependencies And Integration Points
The file depends on Linux `jiffies.h`, `time_after()`, `msecs_to_jiffies()`, `min_t()`, and scheduler timeout APIs. It is suitable for display power sequencing or panel/PHY waits where an earlier timestamp must be honored.

## Risks And Test Signals
Risks include uninterruptible sleep being inappropriate in contexts that must remain killable or atomic; callers must not use these helpers while holding spinlocks or in IRQ context. Timeout off-by-one behavior is intentional to avoid zero waits. Test signals are timing-sensitive panel/power sequencing tests, suspend/resume timing, and lockdep/sleep-in-atomic warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_jiffies.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_limits.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_limits.h

## Purpose
`intel_display_limits.h` defines stable display topology enumerations and maximum counts used across i915 display code. It fixes IDs for pipes, transcoders, planes, ports, HPD pins, AUX channels, and internal color blocks.

## Important APIs, Types, And Functions
Key enums are `enum pipe`, `enum transcoder`, `enum i9xx_plane_id`, `enum plane_id`, `enum port`, `enum hpd_pin`, `enum aux_ch`, and `enum intel_color_block`. Constants such as `I915_MAX_PIPES`, `I915_MAX_TRANSCODERS`, `I915_MAX_PLANES`, `I915_MAX_PORTS`, `HPD_NUM_PINS`, and `INTEL_CB_MAX` size arrays and masks throughout the display subsystem.

## Control Flow And State
There is no runtime flow. The persistent contract is enum numbering. Pipe values start at `PIPE_A = 0` and remain consecutive. `TRANSCODER_A..D` intentionally match corresponding pipe values for 1:1 mappings. Plane IDs are arranged for register macro compatibility, with cursor after numbered universal planes and legacy aliases (`PLANE_PRIMARY`, `PLANE_SPRITE0`, `PLANE_SPRITE1`) mapped onto universal IDs. Port and AUX aliases model Type-C and Xe_LPD repositioned offsets.

## Dependencies And Integration Points
This header is included by most display headers and implementations, especially iterator macros, runtime masks, IRQ arrays, register offset tables, HPD/AUX routing, and color management. Its values are consumed by hardware register macros and bitmask operations, so changing them has broad impact.

## Risks And Test Signals
The main risk is accidental enum renumbering or max-count mismatch, which can corrupt register selection, bit masks, array indexing, and users of pipe/transcoder 1:1 assumptions. Tests include build-time array size coverage, KMS boot on platforms with fused pipes, Type-C/AUX/HPD hotplug tests, plane enumeration checks, and platform bring-up whenever new ports, pipes, transcoders, or color blocks are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_limits.h -->
