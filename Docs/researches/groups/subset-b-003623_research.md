# subset-b-003623 research

Grouped research for i915 core hwmon, initial framebuffer adoption, ioctl compatibility, interrupt dispatch, memory helpers, mitigations, module setup, legacy overlay, panic, module parameters, and PCI device binding files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hwmon.c

## Purpose
Implements the i915 hwmon integration for discrete GPUs. It exposes package temperature, voltage, package power limits, rated power, I1 power/current critical limits, accumulated energy, and fan speed through Linux hwmon sysfs devices for the package and, where supported, per-GT energy devices.

## Important APIs, types, and functions
Key private types are `struct i915_hwmon`, `struct hwm_drvdata`, `struct hwm_reg`, `struct hwm_energy_info`, and `struct hwm_fan_info`. Public entry points are `i915_hwmon_register()`, `i915_hwmon_unregister()`, `i915_hwmon_power_max_disable()`, and `i915_hwmon_power_max_restore()`. The hwmon callbacks are routed through `hwm_is_visible()`, `hwm_read()`, and `hwm_write()`, with per-sensor helpers for temp, input voltage, power, energy, current, and fan. `hwm_get_preregistration_info()` discovers register availability and scale shifts before registration.

## Control flow
Registration exits early for non-dGFX, allocates `i915->hwmon`, initializes shared locking and package/per-GT driver data, snapshots static power-unit scaling and initial counter values, then registers a package hwmon device and optional per-GT energy devices. Reads take runtime PM wakerefs before MMIO or pcode access. Power-limit writes serialize on `hwmon_lock`, wait for any reset-time PL1 disable window, convert user microwatts/milliseconds to hardware fields, and update `PACKAGE_RAPL_LIMIT`.

## State and persistence
Persistent driver state lives in `i915->hwmon`: register addresses, power/energy/time scale shifts, per-device `hwm_drvdata`, energy accumulator snapshots, fan counter/time snapshots, reset-in-progress flag, and waitqueue. Hardware state persists in PCU package registers and pcode I1 setup. `hwm_energy()` extends 32-bit hardware energy counters into a long-lived software accumulator protected by `hwmon_lock`.

## Dependencies and integration points
Depends on hwmon core, sysfs attributes, runtime PM, intel uncore MMIO, pcode mailbox helpers, GT iteration, PCU/MCHBAR register definitions, and i915 reset flows that call the power-limit disable/restore helpers. Integrates with module/device teardown through `i915_hwmon_unregister()`.

## Risks
Counter wrap handling is lock-sensitive and off-by-one mistakes would skew energy. PL1 disable/restore coordination can block sysfs writers and must wake waiters after reset. Visibility probes call pcode reads and suppress DG1/DG2 unsupported I1 paths. Fan speed is interval-based and returns `-EAGAIN` on zero elapsed time. Wrong register validity or unit shifts can expose bogus sysfs values.

## Test signals
Build with `CONFIG_HWMON`, boot on DG1/DG2 and other dGFX, inspect `/sys/class/hwmon` package and `i915_gtN` devices, read/write `power1_max`, `power1_max_interval`, `power1_crit` or `curr1_crit`, sample `energy1_input` across counter wrap, read fan RPM twice with delay, and exercise GPU reset paths while writing PL1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hwmon.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hwmon.h

## Purpose
Declares the i915 hwmon lifecycle and reset coordination hooks, with no-op inline stubs when hwmon support is not reachable.

## Important APIs, types, and functions
Forward declares `struct drm_i915_private` and `struct intel_gt`. Exposes `i915_hwmon_register()`, `i915_hwmon_unregister()`, `i915_hwmon_power_max_disable()`, and `i915_hwmon_power_max_restore()` under `IS_REACHABLE(CONFIG_HWMON)`.

## Control flow
The header has no runtime control flow. Compile-time configuration selects real declarations or empty inline functions so callers do not need local `#ifdef CONFIG_HWMON` guards.

## State and persistence
No state is defined here. The implementation stores state in `i915->hwmon` and in hardware power registers.

## Dependencies and integration points
Included by hwmon implementation and i915 reset/device lifecycle code. It is the narrow API boundary between generic driver flows and the optional hwmon module.

## Risks
Stub behavior means callers must not rely on `old` being initialized when hwmon is disabled; current implementation only uses it when restore is paired with a successful disable path.

## Test signals
Compile with hwmon enabled, disabled, and as module-reachable to catch declaration/stub mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hwmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_initial_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_initial_plane.c

## Purpose
Adopts firmware/GOP-programmed initial scanout buffers into i915 GEM/framebuffer state so fbdev and display takeover can reuse the boot framebuffer instead of immediately reallocating or corrupting it.

## Important APIs, types, and functions
Exports `i915_display_initial_plane_interface`. Key helpers are `initial_plane_memory_type()`, `initial_plane_phys()`, `initial_plane_vma()`, `i915_alloc_initial_plane_obj()`, `i915_initial_plane_setup()`, `i915_plane_config_fini()`, and `i915_initial_plane_vblank_wait()`.

## Control flow
The allocation path chooses local, stolen-local, or stolen-system memory based on platform, reads the GGTT PTE for the firmware plane base, validates presence/locality/range, creates a preallocated GEM object over the physical memory, sets cache coherency, applies tiling metadata from the framebuffer modifier, then pins a GGTT VMA. It first tries a low GGTT address to avoid high GOP placements conflicting with GuC top reservations, reserving the original range to prevent overlapping PTE corruption, then falls back to the original address if needed. Setup pins and references the VMA in plane state and pins a fence if required.

## State and persistence
State is carried in `struct intel_initial_plane_config`: physical base, memory region, framebuffer, and VMA. The created GEM object represents pre-existing memory and the VMA remains pinned for scanout until plane config cleanup. `preserve_bios_swizzle` is set when a non-linear modifier is inherited.

## Dependencies and integration points
Depends on GGTT entry decoding, GEM memory regions, stolen/local memory helpers, framebuffer initialization, display initial-plane parent interface, fbdev stolen-size preference, fenceability checks, and vblank wait through display CRTC helpers.

## Risks
Incorrect PTE locality/range validation can map the wrong physical memory. Moving GOP framebuffers in GGTT must avoid overlap with active scanout PTEs. Tiled objects must be map-and-fenceable when fences are needed. Large stolen boot framebuffers may be discarded intentionally to preserve stolen memory for other features.

## Test signals
Boot with firmware framebuffer on integrated, stolen-local, and dGFX/local-memory systems; verify takeover without flicker, fbdev reuse, no GuC-top GGTT conflicts, correct behavior with tiled and linear boot FBs, and cleanup on failed `intel_framebuffer_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_initial_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_initial_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_initial_plane.h

## Purpose
Declares the i915 implementation of the display initial-plane parent interface.

## Important APIs, types, and functions
Exports `i915_display_initial_plane_interface`, a `struct intel_display_initial_plane_interface` implemented in `i915_initial_plane.c`.

## Control flow
No runtime flow exists in the header. Consumers call through the interface table to allocate, set up, wait, and clean up initial plane resources.

## State and persistence
No local state. Interface callbacks manipulate `intel_initial_plane_config`, GEM objects, and VMA references in the implementation.

## Dependencies and integration points
Used by display code that is decoupled from i915-specific GEM details through `display_parent_interface`.

## Risks
Signature drift between the display parent interface and this extern would be caught at build/link time.

## Test signals
Build coverage and boot display takeover paths validate the declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_initial_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioc32.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioc32.c

## Purpose
Provides 32-bit compatibility handling for legacy i915 DRM ioctls on 64-bit kernels, specifically fixing the historical `DRM_I915_GETPARAM` structure pointer-size mistake.

## Important APIs, types, and functions
Defines compat-only `struct drm_i915_getparam32`, `compat_i915_getparam()`, the `i915_compat_ioctls[]` dispatch table, and public `i915_ioc32_compat_ioctl()`.

## Control flow
`i915_ioc32_compat_ioctl()` decodes the DRM ioctl number. Non-driver ioctls are delegated to `drm_compat_ioctl()`. Driver ioctls with a registered compat shim call that shim; otherwise they fall back to normal `drm_ioctl()`. The getparam shim copies the 32-bit request from userspace, converts the 32-bit pointer with `compat_ptr()`, and invokes `i915_getparam_ioctl()` via `drm_ioctl_kernel()` with `DRM_RENDER_ALLOW`.

## State and persistence
No persistent driver state is stored. The shim only translates userspace ABI data for the current ioctl call.

## Dependencies and integration points
Depends on Linux compat helpers, DRM ioctl dispatch, `i915_getparam_ioctl()`, and the file operation compat hook declared in `i915_ioc32.h`.

## Risks
ABI structure layout must remain exact for 32-bit userspace. Missing compat shims for other pointer-sized legacy ioctls would leave fallback behavior to generic DRM handling, which is only safe for ioctls with identical 32/64-bit layouts.

## Test signals
Run 32-bit userspace on a 64-bit kernel and issue `DRM_I915_GETPARAM`, including render-node access. Invalid pointers should return `-EFAULT`; unsupported driver ioctl numbers should follow normal DRM paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioc32.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioc32.h

## Purpose
Declares the 32-bit compat ioctl entry point when `CONFIG_COMPAT` is enabled and provides a `NULL` hook otherwise.

## Important APIs, types, and functions
Forward declares `struct file` and exposes `i915_ioc32_compat_ioctl()` or defines it as `NULL`.

## Control flow
Compile-time configuration selects the real function or no compat callback.

## State and persistence
No state is defined.

## Dependencies and integration points
Included by the i915 file operations setup so the DRM device can install a compat ioctl handler only when supported.

## Risks
The `NULL` macro path must match the expected file-operations field type. Missing `CONFIG_COMPAT` coverage only affects 32-bit processes on 64-bit kernels.

## Test signals
Compile with and without `CONFIG_COMPAT`; run 32-bit ioctl smoke tests when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioctl.c

## Purpose
Hosts small i915 ioctl helpers that do not warrant their own larger subsystem file. Currently it implements whitelisted MMIO register reads for userspace.

## Important APIs, types, and functions
Defines `struct reg_whitelist`, `reg_read_whitelist[]`, and public `i915_reg_read_ioctl()`. The only whitelist entry exposes the render ring timestamp as a 64-bit register across graphics versions 4 through 12.

## Control flow
The ioctl scans the whitelist for an entry matching the requested offset, graphics version range, and alignment. It extracts low offset bits as flags, takes a runtime PM wakeref, then reads using the correct uncore width helper. For 64-bit registers it supports either direct `intel_uncore_read64()` or the `I915_REG_READ_8B_WA` two-32-bit workaround.

## State and persistence
No persistent state is changed. The ioctl returns the sampled MMIO value in the userspace request structure.

## Dependencies and integration points
Depends on DRM ioctl plumbing, i915 runtime PM, uncore MMIO accessors, register definitions for ring timestamps, and graphics-version predicates.

## Risks
The whitelist is a security boundary. Adding registers can expose privileged hardware state or unstable ABI. Alignment and flag validation prevent arbitrary byte-offset reads. Runtime PM coverage is required so timestamp MMIO is valid while the device may be suspended.

## Test signals
Exercise `DRM_IOCTL_I915_REG_READ` for valid timestamp offsets and the 8-byte workaround flag on supported gens; verify unsupported offsets, misaligned flags, and unsupported platforms return `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioctl.h

## Purpose
Declares the small ioctl helper implemented by `i915_ioctl.c`.

## Important APIs, types, and functions
Forward declares `struct drm_device` and `struct drm_file`; exports `i915_reg_read_ioctl()`.

## Control flow
No runtime flow exists in the header. DRM ioctl tables call the declared function.

## State and persistence
No state is defined.

## Dependencies and integration points
Connects the i915 ioctl dispatch table to the register-read implementation.

## Risks
API drift is compile-time visible. The header intentionally avoids exposing whitelist internals.

## Test signals
Build coverage and ioctl table registration validate the declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_iosf_mbi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_iosf_mbi.h

## Purpose
Provides an architecture/configuration abstraction for IOSF MBI access used by i915, allowing the driver to compile on non-x86 or non-IOSF configurations.

## Important APIs, types, and functions
Includes `<asm/iosf_mbi.h>` when `CONFIG_IOSF_MBI` is enabled. Otherwise defines PMIC bus access event constants, forward declares `struct notifier_block`, and supplies empty or success-returning stubs for punit acquire/release/assert and PMIC notifier registration.

## Control flow
Compile-time configuration chooses real IOSF functions or stubs.

## State and persistence
The stub path stores no state and never serializes real hardware access.

## Dependencies and integration points
Used by i915 code that needs IOSF/PUnit/PMIC coordination without making the whole driver x86-only.

## Risks
On platforms that genuinely need IOSF coordination, building without `CONFIG_IOSF_MBI` would make calls no-ops. This is expected only for unsupported/non-x86 paths where the hardware access is not meaningful.

## Test signals
Compile on x86 with IOSF enabled and on non-x86/allmodconfig-style builds without IOSF. Runtime PMIC/PUnit notifier behavior belongs to real IOSF configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_iosf_mbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_irq.c

## Purpose
Implements top-level i915 interrupt installation, teardown, suspend/resume, generation-specific IRQ handlers, common gen2-style IRQ/error register helpers, PMU IRQ accounting, and Ivybridge L3 parity error notification.

## Important APIs, types, and functions
Public APIs are `intel_irq_init()`, `intel_irq_fini()`, `intel_irq_install()`, `intel_irq_uninstall()`, `intel_irq_suspend()`, `intel_irq_resume()`, `intel_irqs_enabled()`, `intel_synchronize_irq()`, `intel_synchronize_hardirq()`, `gen2_irq_reset()`, `gen2_irq_init()`, `gen2_error_reset()`, `gen2_error_init()`, and `gen2_assert_iir_is_zero()`. Handler families include legacy `i915_irq_handler()`, `i965_irq_handler()`, `ilk_irq_handler()`, `valleyview_irq_handler()`, `cherryview_irq_handler()`, `gen8_irq_handler()`, `gen11_irq_handler()`, and `dg1_irq_handler()`.

## Control flow
Install marks IRQs enabled before postinstall, resets generation-specific registers, requests the shared PCI IRQ with the selected handler, and postinstalls GT/display/PM/GU interrupt masks. Handlers generally verify `irqs_enabled`, disable master interrupt delivery or mask level sources, sample pending source registers, acknowledge IIR/status bits in hardware-safe order, dispatch GT/RPS/display/hotplug/audio/error handlers, re-enable master delivery, and increment PMU IRQ count only for handled device interrupts. Suspend resets hardware, flips `irqs_enabled` false, and synchronizes; resume flips true, resets, and postinstalls.

## State and persistence
Persistent state includes `dev_priv->irqs_enabled`, `dev_priv->gen2_imr_mask`, PMU `irq_count`, L3 parity tracking arrays, GT PM GuC event masks, and hardware interrupt mask/identity/error registers. L3 parity work stores pending slice bits until userspace uevents are emitted and parity interrupts are re-enabled.

## Dependencies and integration points
Depends on GT IRQ handlers, display IRQ/hotplug/audio handlers, runtime PM wakeref assertions, PCI IRQ APIs, uncore raw/MMIO access, RPS/GuC PM interrupts, DRM PMU, and display parent IRQ interface `i915_display_irq_interface`.

## Risks
IRQ ordering is race-sensitive: master disable, source sampling, ack, dispatch, and re-enable differ by platform. Some status bits are level/single-buffered, requiring clear-last behavior. DG1 only supports tile 0 in this path. Legacy error bits can stick and are masked to avoid interrupt storms. PMU accounting must not count shared-line interrupts. Runtime suspend relies on IRQ synchronization instead of wakerefs.

## Test signals
Boot and suspend/resume across gen2 through DG1-era hardware, hotplug displays, trigger vblank/pipe events, GT breadcrumbs, RPS interrupts, LPE audio, legacy master errors, and IVB L3 parity paths. Watch for interrupt storms, lost hotplugs, stale IIR warnings, PMU IRQ counts, and correct `synchronize_irq()` behavior during uninstall/suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_irq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_irq.h

## Purpose
Declares i915 top-level IRQ lifecycle APIs and common gen2-style IRQ/error register helpers.

## Important APIs, types, and functions
Exports install/init/fini/uninstall/suspend/resume/synchronize functions, `intel_irqs_enabled()`, gen2 IRQ/error reset/init helpers, `gen2_assert_iir_is_zero()`, and the display IRQ parent interface. It also declares several GT/RPS interrupt helpers implemented elsewhere.

## Control flow
No runtime flow exists in the header; it defines the callable surface for driver lifecycle and display/GT integration.

## State and persistence
No local state. Declared functions operate on `drm_i915_private`, `intel_uncore`, and hardware IRQ registers.

## Dependencies and integration points
Includes `i915_reg_defs.h` for register struct types and is included by interrupt, GT PM, display, and driver lifecycle code.

## Risks
Because the header mixes top-level and GT/RPS declarations, stale prototypes can affect multiple subsystems. Register helper callers must pass the correct register tuple for the platform.

## Test signals
Build coverage plus suspend/resume, driver load/unload, and RPS interrupt tests validate the API wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_jiffies.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_jiffies.h

## Purpose
Provides a timeout conversion helper that avoids zero-jiffy timeouts for positive millisecond values.

## Important APIs, types, and functions
Defines `msecs_to_jiffies_timeout(unsigned int m)`, which calls `msecs_to_jiffies(m)` and returns `min(MAX_JIFFY_OFFSET, j + 1)`.

## Control flow
Inline conversion only. Adding one jiffy gives callers a full timeout interval rather than immediate expiry after rounding.

## State and persistence
No state.

## Dependencies and integration points
Depends on Linux jiffies helpers and is usable by i915 wait/poll code needing conservative timeouts.

## Risks
For very large inputs, saturation at `MAX_JIFFY_OFFSET` avoids overflow. For zero input, the helper still returns one jiffy, so callers needing immediate/no wait should not use it.

## Test signals
Unit or compile-time checks for zero, small positive, and near-maximum millisecond values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_jiffies.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_list_util.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_list_util.h

## Purpose
Provides small list helpers for RCU-aware or batched list manipulation in i915.

## Important APIs, types, and functions
Defines `__list_del_many(struct list_head *head, struct list_head *first)` and `list_is_last_rcu(const struct list_head *list, const struct list_head *head)`.

## Control flow
`__list_del_many()` relinks `first->prev` to `head` and publishes `head->next` with `WRITE_ONCE()`. `list_is_last_rcu()` reads `list->next` with `READ_ONCE()` and compares it to `head`.

## State and persistence
The helpers mutate or observe caller-owned linked lists only.

## Dependencies and integration points
Depends on Linux list primitives and READ/WRITE_ONCE. Intended for code that needs careful compiler/RCU visibility around list links.

## Risks
`__list_del_many()` assumes callers already validated the list segment and locking/RCU discipline. Misuse can corrupt lists. The helper name is double-underscore to signal low-level semantics.

## Test signals
Build coverage and list-manipulation stress tests under lockdep/KCSAN where used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_list_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_memcpy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_memcpy.c

## Purpose
Implements accelerated reads from write-combining memory using SSE4.1 `movntdqa`, with aligned and mostly-unaligned variants for i915 buffer readback paths.

## Important APIs, types, and functions
Public functions are `i915_memcpy_init_early()`, `i915_memcpy_from_wc()`, and `i915_unaligned_memcpy_from_wc()`. Private helpers `__memcpy_ntdqa()` and `__memcpy_ntdqu()` perform inline assembly copies inside `kernel_fpu_begin()/end()`. `has_movntdqa` is a static key.

## Control flow
Early init enables the static key only when the CPU supports SSE4.1 and is not running under a hypervisor. The aligned copy rejects any source, destination, or length not 16-byte aligned and returns whether acceleration was possible. The unaligned copy first copies bytes until the source is 16-byte aligned, then uses unaligned stores and rounded-up 16-byte reads for the remainder.

## State and persistence
The only persistent state is the `has_movntdqa` static branch. Copy operations do not store driver state.

## Dependencies and integration points
Depends on x86 FPU APIs, cpufeature checks, static branches, and callers that map WC memory and can satisfy alignment/read-past-end guarantees.

## Risks
FPU usage in kernel context must be bracketed correctly. `i915_unaligned_memcpy_from_wc()` assumes callers provide valid memory for a possible 16-byte read past the requested end. Hypervisor emulation gaps intentionally disable the fast path. Non-x86 builds would need equivalent support elsewhere.

## Test signals
Call `i915_has_memcpy_from_wc()`, aligned and misaligned copies, readback correctness from WC mappings, KVM guest behavior, and debug builds where `CI_BUG_ON()` catches invalid unaligned use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_memcpy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_memcpy.h

## Purpose
Declares accelerated WC memcpy helpers and convenience probes for capability/alignment.

## Important APIs, types, and functions
Exports `i915_memcpy_init_early()`, `i915_memcpy_from_wc()`, `i915_unaligned_memcpy_from_wc()`, and macros `i915_can_memcpy_from_wc()` and `i915_has_memcpy_from_wc()`.

## Control flow
The macros call `i915_memcpy_from_wc()` with synthetic low-bit arguments or NULL/zero arguments to test alignment and static-key availability without copying.

## State and persistence
No state in the header. Runtime capability lives in the implementation static key.

## Dependencies and integration points
Included by GEM/display readback code needing WC copy acceleration.

## Risks
The capability macros rely on implementation behavior that returns false for low-bit alignment failures and true for zero-length supported fast path. Changing that contract can break callers.

## Test signals
Build and runtime checks for macro results on SSE4.1 bare metal, hypervisors, and misaligned offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_memcpy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mitigations.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mitigations.c

## Purpose
Implements the `i915.mitigations` module parameter and the query for whether residual thread-local register clearing should be enabled.

## Important APIs, types, and functions
Public `i915_mitigate_clear_residuals()` reads the mitigation bitmask. Private `mitigations_set()` parses parameter strings, `mitigations_get()` formats active state, and `module_param_cb_unsafe()` registers the parameter.

## Control flow
The bitmask defaults to all bits set (`auto`). Parsing duplicates the input, tokenizes comma-separated values, handles first-token `auto` or `off`, accepts `!` and `no` prefixes to disable named mitigations, and updates the mask with `WRITE_ONCE()` only after successful parsing. The getter prints `off`, `auto` plus disabled exceptions, or enabled named mitigations.

## State and persistence
Global `mitigations __read_mostly` stores the active mitigation mask for all Intel GPUs. It persists for the module lifetime and is read locklessly.

## Dependencies and integration points
Depends on Linux module parameter APIs and is consumed by context-switch or workaround code that checks `i915_mitigate_clear_residuals()`.

## Risks
The parser is an ABI: unknown names reject the whole update. `module_param_cb_unsafe` signals runtime changes may not be synchronized with all users. The `auto` representation uses high bits to distinguish default from explicit masks.

## Test signals
Boot or modprobe with `mitigations=auto`, `off`, `residuals`, `auto,noresiduals`, `!residuals`, and invalid names; verify sysfs formatting and residual-clear behavior on affected Ivybridge/Baytrail/Haswell platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mitigations.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mitigations.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mitigations.h

## Purpose
Declares the mitigation query used by i915 code that needs to know whether to clear residual GPU state.

## Important APIs, types, and functions
Exports `bool i915_mitigate_clear_residuals(void);`.

## Control flow
No header runtime flow.

## State and persistence
No state in the header; implementation reads the global mitigation bitmask.

## Dependencies and integration points
Included by workaround/context code and by `i915_mitigations.c`.

## Risks
The single-function API hides parsing details and should stay narrow unless more mitigation categories become externally queried.

## Test signals
Build coverage and runtime checks of mitigation-controlled code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mitigations.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mm.c

## Purpose
Provides low-level helpers to remap IO memory or scatter-gather backed GPU memory into userspace VMAs using special PFN PTEs.

## Important APIs, types, and functions
Public functions are x86-only `remap_io_mapping()` and generic `remap_io_sg()`. Private `struct remap_pfn`, `remap_pfn()`, `remap_sg()`, `sgt_pfn()`, and `EXPECTED_FLAGS` manage page-table application and unwind.

## Control flow
Both remap functions assert expected VMA flags (`VM_PFNMAP | VM_DONTEXPAND | VM_DONTDUMP`). `remap_io_mapping()` combines io_mapping cache attributes with the VMA pgprot and applies sequential PFNs. `remap_io_sg()` initializes an `sgt_iter`, skips to the requested page offset, flushes cache for PFN-based mappings, then applies PTEs over the requested range. On failure both zap the partially inserted special range.

## State and persistence
No driver-global state. The persistent result is user page-table mappings in the target VMA. `remap_pfn.pfn` tracks how many pages were inserted for unwind.

## Dependencies and integration points
Depends on Linux MM `apply_to_page_range()`, special PTE helpers, scatterlist iteration, io_mapping cache attributes, and i915 GEM mmap paths.

## Risks
Callers must hold the proper mmap lock as noted. Incorrect VMA flags or cache attributes can create unsafe mappings. The `iobase == -1` sentinel switches between DMA and PFN addressing. Partial failure unwind must zap the exact inserted range.

## Test signals
Mmap GEM objects backed by contiguous IO mappings and scatter-gather lists, validate cache behavior, page faults/readback, invalid offsets, non-x86 stub behavior, and error injection in `apply_to_page_range()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mm.h

## Purpose
Declares i915 IO remapping helpers and supplies a non-x86 fallback for `remap_io_mapping()`.

## Important APIs, types, and functions
Exports `remap_io_mapping()` on x86, a warning inline stub elsewhere, and `remap_io_sg()` on all builds.

## Control flow
Compile-time architecture selection controls whether real io_mapping remap support is available.

## State and persistence
No header state.

## Dependencies and integration points
Forward declares VMA, io_mapping, and scatterlist types for GEM mmap callers.

## Risks
The non-x86 stub returns success after warning, which is only acceptable if callers do not rely on it for real mappings on unsupported architectures.

## Test signals
Compile on x86 and non-x86 configurations; mmap tests cover the implementation path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mmio_range.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mmio_range.c

## Purpose
Implements a simple lookup helper for sentinel-terminated MMIO address range tables.

## Important APIs, types, and functions
Exports `i915_mmio_range_table_contains(u32 addr, const struct i915_mmio_range *table)`.

## Control flow
Iterates entries until both `start` and `end` are zero, returning true if `addr` falls inclusively between an entry's start and end.

## State and persistence
No state.

## Dependencies and integration points
Depends on `struct i915_mmio_range` from the header. Used by register-filtering code such as shadow/MCR/table checks.

## Risks
Tables cannot represent a valid range starting and ending at zero because that is the sentinel. Inclusive end semantics must match table authors' expectations.

## Test signals
Unit-style tests for first, middle, boundary, absent, and sentinel entries; build coverage for all table users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mmio_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mmio_range.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mmio_range.h

## Purpose
Defines the MMIO range table entry type and containment API.

## Important APIs, types, and functions
Defines `struct i915_mmio_range { u32 start; u32 end; }` and declares `i915_mmio_range_table_contains()`.

## Control flow
No runtime flow in the header.

## State and persistence
No state; callers provide static or dynamic sentinel-terminated tables.

## Dependencies and integration points
Included by MMIO validation/filtering code.

## Risks
Callers must terminate tables with `{ 0, 0 }` and use inclusive end addresses consistently.

## Test signals
Compile table users and test containment boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mmio_range.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_module.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_module.c

## Purpose
Defines the i915 kernel module initialization and exit sequence, including KMS disable checks, subsystem module setup, PCI driver registration, selftests, and perf sysctl registration.

## Important APIs, types, and functions
Key functions are `i915_check_nomodeset()`, `i915_init()`, and `i915_exit()`. `init_funcs[]` is an ordered table of init/exit pairs for active tracking, contexts, GEM contexts, objects, requests, scheduler, VMA, VMA resources, mock selftests, PCI driver, and perf sysctl.

## Control flow
Init iterates `init_funcs[]`, unwinding previously initialized entries in reverse order on negative error. Positive return is treated as an early successful exit only for entries without exit callbacks. `init_progress` records how far init reached, and module exit unwinds from `init_progress - 1` down to zero. `i915_check_nomodeset()` handles deprecated `i915.modeset` and global firmware-only `nomodeset` behavior.

## State and persistence
Global `init_progress` persists module initialization depth. Registered subsystem caches, PCI driver state, and perf sysctls persist until module exit or unwind.

## Dependencies and integration points
Depends on many i915 subsystem module init/exit APIs, `i915_modparams`, DRM firmware-driver-only mode detection, PCI registration, selftest configuration, and module metadata macros.

## Risks
Ordering is important: later subsystems may depend on earlier slab/cache/context/request infrastructure. Positive early exits with exit callbacks are warned because partial teardown would be undefined. Deprecated modeset handling must preserve historical boot behavior.

## Test signals
Module load/unload, failure injection at each init stage to verify unwind, `nomodeset` and `i915.modeset=0/-1/1` boot cases, selftest failures, and perf sysctl registration cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_overlay.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_overlay.c

## Purpose
Implements the i915 backend for the legacy hardware overlay plane parent interface, including overlay register storage, command submission for on/continue/off flips, frontbuffer tracking, framebuffer pinning, and cleanup.

## Important APIs, types, and functions
Exports `i915_display_overlay_interface`. Private `struct i915_overlay` tracks context, current/old VMA, frontbuffer, register BO/iomap, flip address, active bits, and `i915_active last_flip`. Key functions are `i915_overlay_on()`, `i915_overlay_continue()`, `i915_overlay_off()`, `i915_overlay_release_old_vid()`, `i915_overlay_pin_fb()`, `i915_overlay_obj_lookup()`, `i915_overlay_setup()`, and `i915_overlay_cleanup()`.

## Control flow
Setup allocates overlay state, uses RCS0 kernel context, initializes active tracking, allocates a stolen or internal page for overlay registers, pins/iomaps it, and stores either physical or GGTT flip address. On/continue/off allocate requests on the kernel context, emit `MI_OVERLAY_FLIP` and wait commands, update frontbuffer/VMA tracking, and wait for `last_flip` when synchronous completion is needed. Retire callbacks release old VMAs, signal frontbuffer flips, clear active bits on off, and restore i830 clock gating.

## State and persistence
`i915->overlay` persists while setup is active. Overlay register memory persists in `reg_bo`; current and old frame VMAs are pinned across flips; frontbuffer tracking persists for invalidation; `frontbuffer_bits` indicates active overlay ownership.

## Dependencies and integration points
Depends on GEM internal/stolen allocation, GGTT pinning/iomap, RCS requests/ring commands, i915_active retirement, WW locking for display-plane pinning, frontbuffer tracking, PCI config clock-gating workaround, and display overlay parent interface.

## Risks
Legacy overlay sequencing is hardware-sensitive. Old VMAs must not be unpinned before flip completion. Signal interruptions must make forward progress by waiting on the active tracker. Tiled overlay images are rejected. i830 requires clock-gating workarounds. Cleanup assumes display teardown has disabled the overlay.

## Test signals
Exercise legacy overlay ioctls on supported gen2/3 hardware, on/continue/off transitions, signal interruption recovery, old-frame release with and without pending ISR bit, tiled-buffer rejection, stolen/internal register allocation fallback, and module unload after overlay teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_overlay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_overlay.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_overlay.h

## Purpose
Declares the i915 legacy overlay parent interface implementation.

## Important APIs, types, and functions
Exports `i915_display_overlay_interface`.

## Control flow
No runtime flow in the header; display overlay code invokes callbacks through the interface.

## State and persistence
No header state. Implementation stores overlay state in `i915->overlay`.

## Dependencies and integration points
Included by i915 overlay implementation and display glue that consumes `intel_display_overlay_interface`.

## Risks
Interface signature drift is caught at build time.

## Test signals
Build coverage and legacy overlay setup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_overlay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_panic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_panic.c

## Purpose
Adapts i915 GEM framebuffer objects to the DRM panic display infrastructure.

## Important APIs, types, and functions
Exports `i915_display_panic_interface`. Private callbacks are `intel_panic_alloc()`, `intel_panic_setup()`, and `intel_panic_finish()`.

## Control flow
Allocation delegates to `i915_gem_object_alloc_panic()`. Setup retrieves the `intel_framebuffer` from the scanout buffer private pointer, gets its GEM object, and calls `i915_gem_object_panic_setup()` with the framebuffer's panic tiling. Finish delegates to `i915_gem_object_panic_finish()`.

## State and persistence
No local persistent state. Panic mapping/setup state is owned by GEM panic helpers and the `intel_panic` object.

## Dependencies and integration points
Depends on DRM panic, display parent interface, intel framebuffer helpers, and i915 GEM object panic operations.

## Risks
Panic paths run in constrained contexts, so callbacks must stay minimal and avoid normal sleeping/display state assumptions. The scanout buffer private pointer must really be an `intel_framebuffer`.

## Test signals
DRM panic screen tests on i915 scanout buffers, tiled and linear framebuffer panic setup, and build coverage with panic infrastructure enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_panic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_panic.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_panic.h

## Purpose
Declares the i915 DRM panic parent interface.

## Important APIs, types, and functions
Exports `i915_display_panic_interface`.

## Control flow
No runtime flow in the header.

## State and persistence
No state.

## Dependencies and integration points
Included by display panic glue and implementation code.

## Risks
Only interface signature drift risk.

## Test signals
Build coverage and DRM panic setup on i915.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_panic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_params.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_params.c

## Purpose
Defines i915 module parameters, their descriptions and permissions, dynamic debug class mapping, and helper routines to dump/copy/free parameter sets.

## Important APIs, types, and functions
Defines global `i915_modparams` from `I915_PARAMS_FOR_EACH`. Registers parameters such as `modeset`, `reset`, `error_capture`, `enable_hangcheck`, `force_probe`, `memtest`, `mmio_debug`, `enable_guc`, firmware paths, GVT, request timeout, LMEM sizes, and debug-only API. Public helpers are `i915_params_dump()`, `i915_params_copy()`, and `i915_params_free()`.

## Control flow
Macro wrappers register safe and unsafe module params with sysfs permissions and descriptions. Dumping uses `_Generic` to choose type-specific printing. Copying performs a struct copy then duplicates `char *` members; freeing releases only allocated `char *` members and nulls them.

## State and persistence
`i915_modparams __read_mostly` persists module-wide. Copied parameter structs may own duplicated string members and must be released with `i915_params_free()`.

## Dependencies and integration points
Depends on Linux module parameter APIs, DRM printing, dynamic debug class maps, Kconfig feature guards, and consumers throughout driver probe, GT firmware loading, reset, hangcheck, memory sizing, and debugfs.

## Risks
Permissions are ABI-sensitive; comments require most sysfs params to stay read-only, with runtime changes through debugfs. Unsafe params may change without full synchronization. String copy/free ownership must be respected to avoid leaks or double frees. Defaults in the header macro and module_param declarations must stay aligned.

## Test signals
Inspect `/sys/module/i915/parameters`, dump params in driver logs/debugfs, load with custom GuC paths, force_probe, reset, LMEM sizes, and invalid values; run Kconfig combinations for optional params.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_params.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_params.h

## Purpose
Defines the canonical i915 module parameter list, `struct i915_params`, GuC enable bit masks, and parameter helper declarations.

## Important APIs, types, and functions
Defines `ENABLE_GUC_SUBMISSION`, `ENABLE_GUC_LOAD_HUC`, `ENABLE_GUC_MASK`, `I915_PARAMS_FOR_EACH(param)`, `struct i915_params`, global `i915_modparams`, and dump/copy/free prototypes.

## Control flow
The macro list is expanded by the implementation to initialize defaults, declare struct members, register parameters, print, copy, and free fields.

## State and persistence
The struct stores persistent module and per-device copied parameter state. Character pointer fields may either reference static defaults or allocated copies depending on copy/free lifecycle.

## Dependencies and integration points
Included broadly by i915 probe, GT, firmware, memory, debugfs, and module code needing parameter values.

## Risks
The macro is a single source of truth; reordering affects struct layout and comments note bools are kept at the end to avoid holes. Mode values control debugfs creation and sysfs behavior.

## Test signals
Build all macro expansion sites and verify default values/permissions appear as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pci.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pci.c

## Purpose
Defines i915 PCI device matching, platform/device-info tables from gen2 through Meteor Lake/Arrow Lake-era IDs, force-probe policy, PCI resource validation, driver probe/remove/shutdown, and PCI driver registration.

## Important APIs, types, and functions
Public APIs are `i915_pci_register_driver()`, `i915_pci_unregister_driver()`, and `i915_pci_resource_valid()`. Key data includes many `struct intel_device_info` instances, feature macros (`GEN*_FEATURES`, `DGFX_FEATURES`, `XE_HP_FEATURES`), `pciidlist[]`, and `i915_pci_driver`. Probe helpers include `device_id_in_list()`, `id_forced()`, `id_blocked()`, `intel_mmio_bar_valid()`, `i915_pci_probe()`, `i915_pci_remove()`, and `i915_pci_shutdown()`.

## Control flow
PCI matching selects a device-info struct from `pciidlist`, ordered from specific to general. Probe enforces `require_force_probe`, honors negative force-probe block lists, taints the kernel when forcing unsupported IDs, rejects non-zero PCI functions, validates the MMIO BAR for the platform graphics IP, defers to display-driver probe dependency checks, calls `i915_driver_probe()`, then runs live and perf selftests with cleanup on failure. Remove calls `i915_driver_remove()` and clears drvdata. Shutdown delegates to `i915_driver_shutdown()`.

## State and persistence
Static device-info tables persist for the module lifetime and seed runtime platform state during probe. PCI driver registration persists with the kernel PCI core until unregister. Force-probe strings come from `i915_modparams`.

## Dependencies and integration points
Depends on DRM PCI ID macros, platform/device info structures, display probe defer logic, i915 driver probe/remove/shutdown, selftests, PCI resource APIs, force_probe module parameter, and PM ops.

## Risks
Device-info flags are foundational; wrong engine masks, memory regions, PAT/cache mappings, PPGTT sizes, or force-probe flags can break entire platforms. ID ordering matters for subsystem-specific matches. BAR validation must use the correct MMIO BAR by IP version. Force-probing unsupported hardware intentionally taints the kernel.

## Test signals
PCI ID binding across supported platforms, force_probe allow/block strings including `*` and `!*`, non-function-0 rejection, invalid BAR handling, probe defer, live/perf selftest failure cleanup, suspend/shutdown callbacks, and module unload unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pci.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pci.h

## Purpose
Declares the i915 PCI driver registration helpers and PCI BAR/resource validation helper.

## Important APIs, types, and functions
Forward declares `struct pci_dev`; exports `i915_pci_register_driver()`, `i915_pci_unregister_driver()`, and `i915_pci_resource_valid()`.

## Control flow
No runtime flow in the header.

## State and persistence
No header state. The implementation owns the static `pci_driver` and ID table.

## Dependencies and integration points
Used by module init/exit and probe support code.

## Risks
Registration helpers must remain paired by module init unwind. Resource validation semantics are shared with probe code.

## Test signals
Build coverage, module load/unload, and probe BAR validation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pci.h -->
