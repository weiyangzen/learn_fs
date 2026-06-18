# Research: subset-b-003587

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_params.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_params.c

Purpose: implements the i915 display module-parameter backing store, module parameter registration, debug dumping, and safe per-device copies of display parameters. It centralizes display-only knobs such as DMC/VBT firmware overrides, DC-state policy, power-well policy, DSB/DPT/SAGV/IPS feature toggles, backlight behavior, MST, FBC, PSR, Panel Replay, and DMC wakelock behavior.

Important APIs, types, and functions: `intel_display_modparams` is the static `__read_mostly` default instance generated from `INTEL_DISPLAY_PARAMS_FOR_EACH()`. `intel_display_param_named()` and `_unsafe()` wrap `module_param_named*()` plus `MODULE_PARM_DESC()`. `intel_display_params_dump()` prints every parameter through a C11 `_Generic` dispatcher. `intel_display_params_copy()` copies defaults into a caller-owned `struct intel_display_params` and duplicates `char *` members with `kstrdup(..., GFP_ATOMIC)`. `intel_display_params_free()` frees only allocated string fields.

Control flow: compile-time macro expansion creates the default struct initializer and each module parameter declaration. At driver instance setup, callers copy the global module state into display instance state; at debug or logging time, `intel_display_params_dump()` iterates the same parameter list and prints typed values. Cleanup calls the generated free loop to release duplicated string parameters.

State and persistence: persistent kernel state is the global module-parameter object and any per-display copies. String parameters are intentionally duplicated so later per-device lifetime cleanup can free them without owning the global module parameter storage. Module parameter sysfs permissions are mostly read-only; runtime adjustment is expected through i915 debugfs when supported by the parameter's debugfs mode.

Dependencies and integration points: depends on Linux `moduleparam`, slab allocation, `string_choices`, and DRM printer helpers. The header-provided parameter list is the single source of truth shared with debugfs and display instance initialization. The values feed many display subsystems, especially DMC loading, runtime PM/DC states, power wells, panel/backlight code, PSR/FBC/Panel Replay, and DisplayPort MST.

Risks: because the list drives module params, defaults, dumping, copying, and freeing, adding a parameter with a type not covered by the `_Generic` helpers breaks build-time dispatch. `GFP_ATOMIC` duplication can fail, leaving a null string copy if memory is tight. Unsafe module params are read-only in sysfs by convention, but still affect early hardware policy and can put the driver into unsupported test modes.

Test signals: build coverage catches unsupported parameter types and macro expansion mistakes. Runtime signals include `i915.<param>=...` dump output, sysfs module parameter presence/permissions, debugfs parameter behavior, and boot logs for bad firmware paths or invalid DC/power-well settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_params.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_params.h

Purpose: declares the display module-parameter schema and the public helpers used to dump, copy, and free i915 display parameters. It is the canonical list of display-specific runtime and boot-time tuning knobs.

Important APIs, types, and functions: `INTEL_DISPLAY_PARAMS_FOR_EACH(param)` enumerates every parameter as `(type, name, default, debugfs_mode)`. `struct intel_display_params` is generated from that macro, ensuring field layout matches the parameter schema. Exported prototypes are `intel_display_params_dump()`, `intel_display_params_copy()`, and `intel_display_params_free()`.

Control flow: including code supplies a function-like macro to `INTEL_DISPLAY_PARAMS_FOR_EACH()` to generate declarations, struct members, initialization, dump loops, debugfs entries, or cleanup loops. The schema includes both boot-only/read-mostly policy fields and debugfs-writable feature toggles via the `mode` argument.

State and persistence: this header defines the in-memory shape of per-display parameter state. It does not store state directly, but every field becomes part of the driver's display configuration for the life of a display instance. Pointer fields require copy/free handling in the implementation.

Dependencies and integration points: depends on Linux integer/bool types and forward-declares `struct drm_printer`. It is included by parameter implementation code and by display initialization paths that need `display->params`. Integration is broad because fields influence firmware loading, display power management, connector probing, panel policy, display compression, and link features.

Risks: the macro list is order- and type-sensitive. A new type must be supported by all macro users in `intel_display_params.c` and any debugfs code. Debugfs mode values must be chosen carefully because some parameters are not safe to mutate after hardware initialization. Default changes can alter platform power behavior before tests reach modeset paths.

Test signals: compile errors from macro users reveal unsupported schema changes. Runtime validation comes from module parameter defaults, debugfs file modes, parameter dump output, and targeted tests that boot with non-default i915 display parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power.c

Purpose: orchestrates i915 display power domains at the policy/refcount level. It maps logical display domains to power wells, manages runtime PM wakerefs, async power-down batching, display DC-state policy, DBUF/CDCLK/display-core init and uninit flows, suspend/resume sequencing, debug reporting, and port/AUX-to-power-domain translation.

Important APIs, types, and functions: public entry points include `intel_power_domains_init()`, `intel_power_domains_init_hw()`, `intel_power_domains_enable()`, `intel_power_domains_disable()`, `intel_power_domains_suspend()`, `intel_power_domains_resume()`, `intel_power_domains_driver_remove()`, `intel_power_domains_sanitize_state()`, `intel_display_power_get()`, `intel_display_power_get_if_enabled()`, `intel_display_power_put()`, `__intel_display_power_put_async()`, `intel_display_power_flush_work()`, `intel_display_power_set_target_dc_state()`, `intel_display_power_get_current_dc_state()`, `intel_display_power_suspend_late()`, `intel_display_power_resume_early()`, `intel_display_power_suspend()`, `intel_display_power_resume()`, `intel_display_power_debug()`, and the DDI/AUX domain lookup helpers. Internal pivots are `__intel_display_power_get_domain()`, `__intel_display_power_put_domain()`, `intel_display_power_put_async_work()`, `get_allowed_dc_mask()`, platform display-core init/uninit functions, and `gen9_dbuf_slices_update()`.

Control flow: initialization sanitizes `disable_power_well`, derives `allowed_dc_mask`, initializes mutex/work state, and calls `intel_display_power_map_init()`. Hardware init runs platform-specific display-core setup, takes `POWER_DOMAIN_INIT` to hold all init-needed wells through HW readout, optionally takes another init ref when power-well toggling is disabled, then syncs all power wells. Normal clients take one logical domain; the code grabs a display RPM wakeref, resolves all wells containing that domain, increments well counts in enable order, and later decrements in reverse order. Async put holds an extra raw RPM wakeref, records domains in two pending bitmaps, and releases the final refs from delayed work unless a later get reclaims the pending ref.

State and persistence: `struct i915_power_domains` owns `initializing`, `display_core_suspended`, `dc_state`, `target_dc_state`, `allowed_dc_mask`, init/disable wakerefs, per-domain use counts, async put bitmaps, delayed work, and the allocated power-well array. Hardware state persists in power-well registers, DC_STATE_EN, DBUF registers, CDCLK, PHY state, PCH reset handshake bits, and DMC-controlled state. There is no disk persistence; state is reconstructed on driver init and resume.

Dependencies and integration points: depends on the power map and well operation layers, runtime PM wrappers, DMC/DMC wakelock, CDCLK, DBUF/watermark, PCH refclk, combo/SNPS PHY, pcode, display workarounds, PSR, DRAM info, parent IRQ/PC8 helpers, and DRM debug infrastructure. Modeset readout and sanitization are expected to acquire domain refs for active hardware before unused BIOS-enabled wells are disabled.

Risks: refcount mismatches can leave display hardware unpowered during MMIO access or block runtime/system low-power states. Async put requires disjoint pending masks and careful RPM wakeref ownership. DC-state programming interacts with DMC firmware and may be ignored or delayed; the code logs mismatches. Platform init/uninit sequences are order-sensitive around DC9/PC8, CDCLK, DBUF, PHY, DMC program load/disable, PCH reset handshake, and workarounds. Port/AUX lookup fallback domains are warning paths and can hide platform table errors.

Test signals: debug runtime PM builds verify well refcounts, domain counts, async state, and HW enabled state. Useful runtime signals include `intel_display_power_debug()` output, `drm_dbg_kms` DC-state transitions, warnings from DBUF/CDCLK verification, DMC DC6 allowed-count changes, suspend/resume DC9 or PC8 logs, and failures from `intel_de_wait_*()` polling. CI should exercise boot, modeset readout, connector hotplug, DP AUX on combo/TC ports, runtime suspend, S0ix/system suspend, and module parameters `enable_dc` and `disable_power_well`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power.h

Purpose: declares the logical display power-domain model and public power-management API for i915 display code. It is the contract clients use to keep pipes, transcoders, ports, AUX channels, audio, VGA, GT IRQ, DC-off, TC-cold, and initialization resources powered while accessing hardware.

Important APIs, types, and functions: `enum intel_display_power_domain` lists all logical domains and relies on consecutive pipe/transcoder/port ranges for helper macros. `struct intel_power_domain_mask` wraps a bitmap. `struct i915_power_domains` stores global power-domain state, per-domain use counts, async put state, and the power-well array. `struct intel_display_power_domain_set` groups acquired refs for batch release. Public APIs cover init/cleanup, HW init/remove, enable/disable, suspend/resume, domain get/put, async put, set-based acquisition/release, debug output, DDI/AUX domain translation, and DBUF slice updates. RAII-style macros `with_intel_display_power()` and `with_intel_display_power_if_enabled()` acquire a domain for a loop scope and release asynchronously.

Control flow: display clients include this header, choose the innermost logical domain needed, call `intel_display_power_get()` or conditional/set variants before MMIO access, and release with `intel_display_power_put()` or async helpers. Debug runtime PM builds preserve and verify `struct ref_tracker *` wakerefs; non-debug builds collapse wakeref tracking to unchecked put paths.

State and persistence: the header defines in-memory refcount and async-work state but does not implement persistence. Domain use counts are per display instance. The masks and wakeref arrays track acquired domains until explicit release. `INTEL_WAKEREF_DEF` marks non-debug or untracked wakeref slots.

Dependencies and integration points: depends on Linux mutex/workqueue and i915 display type forward declarations. It is consumed across modeset, connector, AUX, audio, VGA, watermarks, and suspend/resume paths. The domain enum must remain synchronized with mapping tables in `intel_display_power_map.c` and platform operation implementations in `intel_display_power_well.c`.

Risks: enum reordering breaks arithmetic macros such as `POWER_DOMAIN_PIPE()` and port/transcoder domain derivation. Missing get/put symmetry leaks power wells or causes MMIO while unpowered. Conditional compilation changes wakeref checking behavior, so bugs may only become visible with `CONFIG_DRM_I915_DEBUG_RUNTIME_PM`.

Test signals: compile coverage catches enum/API drift, while debug runtime PM warns on refcount mismatch. Runtime inspection through debugfs/power debug output, power-domain set release paths, and scoped macro use around MMIO accesses are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_map.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_map.c

Purpose: defines the platform-specific mapping from logical display power domains to concrete power wells. It is the static topology database used by `intel_display_power.c` to allocate per-platform `struct i915_power_well` instances with the correct names, IDs, domain masks, operation tables, IRQ masks, fuse flags, timeout quirks, and enable/disable ordering.

Important APIs, types, and functions: local macros `I915_PW_DOMAINS()`, `I915_DECL_PW_DOMAINS()`, `I915_PW_INSTANCES()`, `I915_PW()`, and `I915_PW_DESCRIPTORS()` compactly define domain lists, instance lists, and descriptor arrays. `struct i915_power_well_desc_list` groups descriptor arrays. `init_power_well_domains()` fills a well bitmap, treating a zero-length list as all domains and NULL as no domains. `__set_power_wells()` counts instances, allocates `power_domains->power_wells`, initializes descriptors/instance indexes/domain masks, and validates unique direct-lookup IDs. `intel_display_power_map_init()` selects the descriptor list for the detected platform. `intel_display_power_map_cleanup()` frees the allocated well array.

Control flow: init returns no wells when `HAS_DISPLAY()` is false. Otherwise it selects from WCL, Xe3LPD, Xe2LPD, Xe_LPD+, DG2/Xe_HPD, Xe_LPD, DG1, ADL-S, RKL, TGL, ICL, GLK, BXT, SKL, CHV, BDW, HSW, VLV, i830, or generic i9xx tables. Ordering in each descriptor list is significant: normal enabling walks lower to higher indexes and disabling walks the reverse path, which encodes parent-before-child power dependencies.

State and persistence: the file contains static const topology tables. Runtime state created here is only the allocated `power_wells` array, `power_well_count`, per-well descriptor pointer, instance index, and domain bitmap. Hardware state is not touched in this file.

Dependencies and integration points: depends on `intel_display_core`/platform flags, display power well types and ops, register index definitions, and VLV IOSF sideband constants. Descriptor `ops` link directly to operation tables exported by `intel_display_power_well.c`; descriptor IDs are consumed by `lookup_power_well()` callers in init/DC/PHY paths.

Risks: an omitted domain leaves hardware unpowered for a logical user; an extra domain keeps wells on and hurts power. Descriptor order mistakes can violate platform dependency chains. Duplicate nonzero IDs are warned through a bitset check. `u8 count` and `u8 instance_idx` assume descriptor/instance counts stay small. The CHV table contains duplicated `POWER_DOMAIN_PIPE_PANEL_FITTER_C`, which is harmless in a bitmap but shows why domain-list review matters.

Test signals: boot on each platform family should allocate the expected number and names of wells in `intel_display_power_debug()` output. Runtime PM debug verification detects mismatched refcounts against domain membership. Platform-specific CI should cover DC-off, AUX, DDI IO, TC cold, PICA, and independent pipe power-gating paths for modern tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_map.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_map.h

Purpose: exposes the minimal interface for building and destroying the platform-specific power-domain to power-well mapping.

Important APIs, types, and functions: forward-declares `struct i915_power_domains` and declares `intel_display_power_map_init()` plus `intel_display_power_map_cleanup()`.

Control flow: callers initialize `struct i915_power_domains` enough to identify the containing display, then call `intel_display_power_map_init()` during power-domain setup and `intel_display_power_map_cleanup()` during teardown.

State and persistence: no state is stored in the header. The implementation allocates and later frees the dynamic power-well array inside `struct i915_power_domains`.

Dependencies and integration points: included by `intel_display_power.c`, with implementation dependencies hidden in `intel_display_power_map.c`. It keeps the topology table private while letting the power-domain core request a ready-to-use mapping.

Risks: failing init must abort display power-domain setup because no safe logical-domain mapping exists. Cleanup must match successful init to avoid leaking the power-well array.

Test signals: build linkage catches signature drift. Runtime init failures, missing power wells, or empty debug output on display-capable platforms indicate map init problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_well.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_well.c

Purpose: implements the hardware-facing operations for each i915 display power-well type. It converts refcount transitions from the power-domain core into MMIO, PUnit, PCODE, DPIO, PHY, AUX, DMC/DC-state, interrupt, and workaround sequences for legacy i9xx/i830, HSW/BDW, VLV/CHV, SKL/BXT/GLK, ICL/TGL/RKL/DG1, Xe_LPD/Xe_HPD, Xe_LPD+, Xe2LPD, Xe3LPD, and WCL-style hardware.

Important APIs, types, and functions: `struct i915_power_well_ops` defines `sync_hw`, `enable`, `disable`, and `is_enabled` callbacks plus optional HSW-style register blocks. Generic exported helpers include `lookup_power_well()`, `intel_power_well_enable()`, `intel_power_well_disable()`, `intel_power_well_sync_hw()`, `intel_power_well_get()`, `intel_power_well_put()`, `intel_power_well_is_enabled()`, cached state/name/domain/refcount accessors, `intel_display_power_well_is_enabled()`, `chv_phy_powergate_ch()`, and `chv_phy_powergate_lanes()`. Exported ops include `i9xx_always_on_power_well_ops`, `i830_pipes_power_well_ops`, `hsw_power_well_ops`, `gen9_dc_off_power_well_ops`, BXT/VLV/CHV DPIO ops, ICL AUX/DDI ops, TGL TC-cold ops, Xe_LPD+ AUX ops, and Xe2LPD PICA ops.

Control flow: the power-domain core increments a well count; the 0-to-1 transition calls the descriptor's enable callback and caches `hw_enabled=true`. The 1-to-0 transition clears the cache and calls disable. HSW-style wells set/clear driver request bits, wait for status, optionally wait for fuses, handle BIOS/KVMR/DMC requesters, and wrap pipe IRQ clock-gating changes. DC-off "enable" disables DC states; DC-off "disable" enables target DC3CO/DC5/DC6 when DMC payload is present. VLV/CHV paths use PUnit power-gate registers and DPIO/PHY reset/override sequences. ICL/TGL AUX paths distinguish combo PHY, TC PHY, and TBT AUX, including TC-cold exit/blocking and DKL uC health waits. Xe_LPD+ AUX and Xe2LPD PICA use dedicated request/status bits and fixed-delay fallbacks where hardware status is unavailable.

State and persistence: per-well software state is `count`, cached `hw_enabled`, descriptor, instance index, and domain bitmap. Additional driver state includes CHV `display->power.chv_phy_control` shadow state because the hardware register may be unsafe to read. Hardware state lives in power-well control registers, PUnit power gate registers, DPIO/PHY registers, `DC_STATE_EN`, DBUF/CDCLK-related state, AUX channel control, TC-cold PCODE state, PICA control, and IRQ gating registers. State is resynchronized during init/resume through `sync_hw` callbacks and platform init code.

Dependencies and integration points: tightly integrated with `intel_display_power_map.c` descriptors, `intel_display_power.c` refcounting/DC policy, runtime PM assertions, display IRQ management, DMC/DMC wakelock, PSR, PPS/backlight, CRT/VGA, hotplug polling, PCode/parent helpers, VLV sideband, DPIO/PHY helpers, TC port reference tracking, DKL PHY, combo PHY, and display workaround checks.

Risks: enable/disable sequences are timing- and ordering-sensitive; missed waits can cause powered-down MMIO, AUX failures, PHY calibration issues, or suspend hangs. HSW disable may leave wells forced on by BIOS, DMC, debug, or KVMR requesters. DC-state writes may need repeated writes and can invalidate PHY/CDCLK/DBUF assumptions. TC/TBT AUX timeouts may be expected in tunnel-down or TC-cold-exit cases, so error handling must distinguish expected and unexpected timeouts. CHV PHY uses shadow state because reading the register is unsafe; any unsynchronized write risks losing lane power state.

Test signals: warnings from `drm_WARN*`, `drm_err`, and `drm_dbg_kms` around power-well timeouts, forced-on requesters, fuse waits, DC-state mismatches, DBUF state, PHY status, DPIO lane powerdown, TC uC health, AUX power status, and PICA timeouts are primary signals. CI should exercise runtime PM get/put, connector detection over combo/TC/TBT AUX, display suspend/resume, DC5/DC6/DC9, VLV/CHV DPIO power transitions, and debug runtime PM refcount verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_well.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_well.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_well.h

Purpose: declares the concrete display power-well data model, iteration helpers, lookup IDs, exported operation tables, and hardware helper APIs used by i915 display power management.

Important APIs, types, and functions: `for_each_power_well()` and reverse iteration traverse the allocated well array. `enum i915_power_well_id` assigns stable IDs for direct lookup of special wells such as VLV display/DPIO, HSW global, SKL MISC_IO/PW1/PW2/DC_off, ICL PW3, TGL TC_cold_off, and BXT/GLK/CHV DPIO wells. `struct i915_power_well_instance` names an instance, links a domain list, carries an ID, and stores platform-specific index/PHY/AUX metadata. `struct i915_power_well_desc` binds ops, instances, IRQ pipe mask, always-on/fuse/fixed-delay/TC-TBT flags, and enable timeout. `struct i915_power_well` is the runtime object with descriptor, domain mask, count, cached HW state, and instance index. The header declares well lookup/refcount/state helpers, CHV lane power-gating helpers, DC-state helpers, and all operation-table externs.

Control flow: mapping tables instantiate descriptors and instances declared by this header, the power-domain core iterates and refcounts `struct i915_power_well`, and the operation implementation dereferences instance metadata to program the correct hardware. Special init and suspend paths use direct IDs through `lookup_power_well()`.

State and persistence: the runtime well object persists for the display instance lifetime after map initialization. It stores software refcounts and cached state only; hardware persistence is in platform registers controlled by operation callbacks.

Dependencies and integration points: includes `intel_display_power.h` for domain masks and `intel_dpio_phy.h` for DPIO metadata. It is shared by map, core, and operation implementation files, and by display code that needs direct power-well state such as DC and CHV PHY management.

Risks: descriptor fields are compact bitfields and small integers, so new platforms must fit counts/timeouts or adjust types. Direct lookup IDs must remain unique and are only assigned to wells that callers bypass through the domain framework. `for_each_power_well_reverse()` assumes at least one well when used, so callers must respect no-display cases. Cached enabled state can be stale if hardware changes outside the framework.

Test signals: compiler/linker coverage for extern ops, runtime debug output listing names/refcounts/domains, warnings for missing IDs in `lookup_power_well()`, and debug PM verification of cached/refcount/HW state consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_well.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_reg_defs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_reg_defs.h

Purpose: provides display-register address helper macros layered on top of generic i915 register definitions. It gives display code concise, typed helpers for pipe, plane, transcoder, port, PLL, PHY, and device-info-offset-based MMIO register selection.

Important APIs, types, and functions: `VLV_DISPLAY_BASE` defines the Valleyview display MMIO base. `_PIPE()`, `_PLANE()`, `_TRANS()`, `_PORT()`, `_PLL()`, and `_PHY()` wrap `_PICK_EVEN()` for evenly spaced register instances. `_MMIO_PIPE()`, `_MMIO_PLANE()`, `_MMIO_TRANS()`, `_MMIO_PORT()`, `_MMIO_PLL()`, and `_MMIO_PHY()` convert those offsets to `i915_reg_t`. `_MMIO_BASE_PIPE3()` and `_MMIO_BASE_PORT3()` support two-range offset layouts. `_MMIO_PIPE2()`, `_MMIO_TRANS2()`, and `_MMIO_CURSOR2()` use per-device offset arrays from display device info.

Control flow: register definition headers include these macros to define symbolic registers. Runtime code passes pipe/transcoder/port/etc. indexes and receives an MMIO register token suitable for `intel_de_read()`, `intel_de_write()`, and `intel_de_rmw()`.

State and persistence: no runtime state is stored. The macros encode address arithmetic, with dynamic offsets coming from `INTEL_DISPLAY_DEVICE_*_OFFSET(display)` accessors when using the `*2` helpers.

Dependencies and integration points: depends on `i915_reg_defs.h` for `_MMIO`, `_PICK_EVEN`, and `_PICK_EVEN_2RANGES`. Integrated across display register headers and all display MMIO code, including the power-management files in this work item.

Risks: incorrect helper selection yields wrong MMIO offsets, which can silently program the wrong pipe/port/PHY register. The `*2` helpers require valid display device-info offset tables. `_MMIO_BASE_PIPE3()` and `_MMIO_BASE_PORT3()` parameter naming is generic and should be reviewed carefully when used for non-pipe selectors.

Test signals: compile-time register definitions catch syntax/type issues, but functional validation comes from platform MMIO read/write behavior, register trace review, and hardware tests that exercise multiple pipes, ports, transcoders, PLLs, and PHYs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_reg_defs.h -->
