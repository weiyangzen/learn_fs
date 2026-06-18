# subset-b-003731 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_i2c.c

## Purpose

`radeon_i2c.c` implements Radeon display I2C/DDC plumbing for legacy and AtomBIOS-era hardware. It probes EDID over DDC or DP AUX, exposes software bit-banged GPIO adapters, selects pre-DCE hardware I2C engines where supported, delegates newer DCE3 hardware I2C to AtomBIOS helpers, registers default buses from AtomBIOS/COMBIOS tables, provides small byte read/write helpers, and programs external DDC/clock-data router muxes on connector paths.

## Important APIs, Types, and Functions

- `radeon_ddc_probe(struct radeon_connector *, bool use_aux)`: selects any DDC router port, performs a two-message EDID read at `DDC_ADDR`, and accepts the bus only when the EDID header has at least six valid leading bytes.
- Bit-bang callbacks `pre_xfer`, `post_xfer`, `get_clock`, `get_data`, `set_clock`, and `set_data`: claim GPIO pins through mask registers, reset problematic legacy hardware I2C state, switch DCE3 pads to DDC mode, and expose pin direction/value operations to `i2c-algo-bit`.
- `radeon_get_i2c_prescale()`: computes legacy hardware-I2C prescale values from `rdev->pm.current_sclk` for R100-R5xx families.
- `r100_hw_i2c_xfer()` and `r500_hw_i2c_xfer()`: program legacy and Avivo hardware I2C controller registers, including address/data FIFO writes, GO/DONE polling, abort handling, pin selection, BIOS scratch busy marking, and 15-byte chunking on R5xx.
- `radeon_hw_i2c_xfer()` / `radeon_hw_i2c_func()`: Linux `i2c_algorithm` hooks that dispatch by ASIC family and advertise normal I2C plus SMBus emulation.
- `radeon_i2c_create()`: chooses a hardware, AtomBIOS-backed, or bit-banged adapter from `struct radeon_i2c_bus_rec`, initializes `struct radeon_i2c_chan`, and registers it with the I2C core.
- `radeon_i2c_init()`, `radeon_i2c_fini()`, `radeon_i2c_add()`, and `radeon_i2c_lookup()`: populate and query `rdev->i2c_bus[]`.
- `radeon_i2c_get_byte()` / `radeon_i2c_put_byte()`: convenience single-register I2C transactions used by router and encoder code.
- `radeon_router_select_ddc_port()` and `radeon_router_select_cd_port()`: program external mux/router control registers through a router I2C bus.

## Control Flow

DDC probing starts by switching any connector router to the desired DDC lane. It then reads the first EDID block bytes through either the connector's DP AUX DDC adapter or normal I2C adapter. A failed two-message transfer or weak EDID header returns `false`; successful probing returns `true`.

For bit-banged transfers, `pre_xfer` serializes the channel with `i2c->mutex`, works around R200-R400 hardware I2C reset issues by selecting a harmless DVI I2C pin under `dc_hw_i2c_mutex`, switches pads and GPIO mask registers to software ownership, clears output values, and sets both clock/data as inputs. The bit algorithm then calls `set_*` and `get_*`; `post_xfer` unclaims GPIO masks and unlocks the bus.

Hardware transfers hold both `dc_hw_i2c_mutex` and `pm.mutex`, because controller timing depends on stable SCLK. R100/R3xx/R4xx code computes prescale and selects the right DDC pin encoding before issuing per-byte transactions. R5xx Avivo code additionally clears GPIO ownership, claims the Avivo I2C arbitration register, saves/restores controller state, and splits reads/writes into controller FIFO chunks. Both paths poll GO/DONE bits with microsecond delays and abort on error before restoring scratch/state.

Adapter creation is policy-driven. Multimedia I2C is exposed only when forced hardware I2C is enabled. Older ASICs and R5xx use the local hardware algorithms when allowed; DCE3 hardware-capable buses use AtomBIOS I2C callbacks; all other buses fall back to GPIO bit-banging.

## State and Persistence Behavior

Persistent state lives in `rdev->i2c_bus[]`, each `radeon_i2c_chan`'s copied bus record, Linux `i2c_adapter` registration, and connector router metadata. Transfer state is transient but mutates hardware GPIO masks, I2C controller registers, DDC pin routing, Avivo arbitration, and `RADEON_BIOS_6_SCRATCH` busy flags. Locks protect channel-local GPIO use, global display-controller hardware I2C use, and PM clock stability.

`radeon_i2c_fini()` only nulls array entries in this snapshot. Adapter lifetime is mostly delegated to devm registration for the legacy hardware path or normal I2C registration for Atom/bit paths; any lifecycle changes must preserve I2C core unregister semantics.

## Dependencies and Integration Points

This file depends on Linux I2C, `i2c-algo-bit`, DRM EDID validation, Radeon register macros, AtomBIOS hardware I2C callbacks declared in `atom.h`, `struct radeon_i2c_bus_rec` and `struct radeon_i2c_chan` from `radeon_mode.h`, BIOS connector parsing (`radeon_atombios_i2c_init` / `radeon_combios_i2c_init`), DP AUX DDC, and connector hotplug/mode-detect code. It interacts with PM (`rdev->pm.current_sclk`, `pm.mutex`) and BIOS scratch state visible to firmware.

## Risks and Edge Cases

- Several ASIC families are marked `todo` for local hardware I2C and currently fall through with success-like `ret = 0` in `radeon_hw_i2c_xfer()` unless another case sets an error, so adapter selection must avoid those paths or callers may see misleading transfers.
- Hardware polling loops can exit after timeout without explicitly checking that `DONE` was observed; a loop that runs to its bound without error status can still continue to cleanup with `ret == num`.
- Prescale calculation depends on `current_sclk`; stale PM state or missing PM locking would corrupt bus timing.
- GPIO and controller register save/restore is chipset-specific and easy to regress during register macro changes.
- `radeon_i2c_fini()` does not explicitly unregister non-devm adapters in this file, so lifetime relies on external cleanup paths or device teardown.
- Router byte helpers log failures but do not propagate errors, so mux selection failure may surface only as later DDC failure.

## Test Signals

Useful validation includes EDID probing over bit-banged DDC, hardware I2C, AtomBIOS I2C, and DP AUX; hotplug detection on connectors with DDC routers; forced `radeon_hw_i2c=1` on supported and unsupported ASICs; lockdep coverage around PM/I2C/display locks; fault injection for NACK/GO timeout/arbitration failure; suspend/resume ensuring scratch busy bits and saved Avivo registers are restored; and regression tests for shared DDC mux systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ib.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ib.c

## Purpose

`radeon_ib.c` manages indirect buffers, the GPU-visible command buffers that userspace command streams are copied into and scheduled through Radeon rings. It allocates IB memory from the ring temporary suballocator, records synchronization and VM metadata, emits IB execution packets and fences, initializes/destroys the shared IB pool, tests rings, and exposes debugfs state for the suballocator.

## Important APIs, Types, and Functions

- `radeon_ib_get()`: allocates a `drm_suballoc` from `rdev->ring_tmp_bo`, initializes `ib->sync`, sets CPU/GPU addresses, associates ring and VM, and handles virtual-address placement at `RADEON_VA_IB_OFFSET`.
- `radeon_ib_free()`: releases sync state, frees the suballocated IB after its fence, and drops the fence reference.
- `radeon_ib_schedule()`: validates length/ring readiness, locks ring space, grabs a VM ID when needed, synchronizes against other rings, emits VM flushes, executes optional SI constant-engine IB before the main IB, emits a fence, attaches it to VM state, and commits the ring.
- `radeon_ib_pool_init()` / `radeon_ib_pool_fini()`: create/start and suspend/finalize the suballocator backing IBs, selecting write-combined GTT only for newer families where appropriate.
- `radeon_ib_ring_tests()`: submits per-ring test IBs, disables failed non-GFX rings, and fails hard when the primary GFX ring IB test fails.
- Debugfs helpers `radeon_debugfs_sa_info_show()` and `radeon_debugfs_sa_init()` expose `radeon_sa_bo_dump_debug_info()` as `radeon_sa_info`.

## Control Flow

IB use begins after `radeon_ib_pool_init()` initializes `rdev->ring_tmp_bo` in GTT and marks `ib_pool_ready`. A caller then obtains an IB with `radeon_ib_get()`, fills `ib->ptr`, sets `length_dw`, and passes it to `radeon_ib_schedule()`.

Scheduling first rejects empty IBs or unready rings. It reserves enough ring space for synchronization and fence packets, optionally obtains a VM ID and folds its fence into the IB sync object, waits/emits synchronization against other rings, and flushes VM page-table state if the IB uses a VM. SI constant IBs are executed first and inherit the main fence. The main IB execution packet is written through `radeon_ring_ib_execute()`, `radeon_fence_emit()` creates completion tracking, VM state is fenced, and `radeon_ring_unlock_commit()` publishes the ring writes with optional HDP cache flush.

Ring self-tests iterate all `RADEON_NUM_RINGS`; failures force fence completion and mark that ring not ready. Failure on the graphics ring disables acceleration and returns the error because the driver cannot operate normally without it.

## State and Persistence Behavior

The IB pool is persistent device state in `rdev->ring_tmp_bo` and the `ib_pool_ready` flag. Individual `struct radeon_ib` objects are caller-owned but contain suballocator state, ring index, CPU pointer, GPU address, VM pointer, sync state, constant-IB flag, and fence pointer. Fences persist past scheduling until all users, suballocations, and sync objects release them. VM ID and VM fence updates persist in the per-file or per-VM GPU address space.

## Dependencies and Integration Points

This file depends on Radeon suballocation (`radeon_sa_bo_*`), ring management, fences, sync objects, VM management, debugfs, and per-ASIC `radeon_ring_ib_execute()`. It is used by command submission, ring tests during device bring-up, UVD/VCE/DMA/GFX engines, and KMS open paths that map the IB pool into per-client VMs.

## Risks and Edge Cases

- `radeon_ib_schedule()` assumes `ib->length_dw` is correctly set by command submission validation before scheduling.
- VM ID acquisition and ring sync errors must undo ring locks; this path uses `radeon_ring_unlock_undo()` before returning, and future changes must preserve that cleanup.
- Constant IBs share the main fence but free their sync object with no fence before execution completes, so ownership rules are subtle.
- Pool initialization returns early if already ready but does not validate size/domain compatibility after family changes or resume transitions.
- Ring test failure clears `needs_reset`, marks rings not ready, and may leave partial acceleration available; user-visible capability reporting must align with this.

## Test Signals

Test signals include successful IB ring tests on all enabled rings, forced ring-test failures disabling only affected non-GFX rings, command submission with and without VM, SI constant/main IB ordering, cross-ring synchronization tests, fence signaling under reset, suballocator exhaustion and delayed free behavior, debugfs `radeon_sa_info` readability, and suspend/resume pool teardown/restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_irq_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_irq_kms.c

## Purpose

`radeon_irq_kms.c` implements KMS interrupt setup and interrupt-source reference management. It installs the shared PCI interrupt handler, configures MSI policy, initializes vblank support, schedules hotplug/DisplayPort/audio work outside hard IRQ context, exposes helpers for enabling/disabling software fence interrupts, page-flip/vblank interrupts, AFMT audio interrupts, and hotplug-detect pins, and provides a small register update helper for per-ASIC IRQ code.

## Important APIs, Types, and Functions

- `radeon_driver_irq_handler_kms()`: DRM IRQ handler wrapper that calls the per-ASIC `radeon_irq_process()` callback and updates runtime PM activity when an IRQ was handled.
- `radeon_hotplug_work_func()` and `radeon_dp_work_func()`: deferred connector walks that call `radeon_connector_hotplug()` under mode-config locking; hotplug work also sends a DRM HPD uevent.
- `radeon_driver_irq_preinstall_kms()`, `radeon_driver_irq_postinstall_kms()`, and `radeon_driver_irq_uninstall_kms()`: reset software IRQ state, program hardware IRQ masks, clear pending bits, and set vblank counter width.
- `radeon_irq_install()` / `radeon_irq_uninstall()`: request/free the shared PCI IRQ around the DRM/Radeon pre/post/uninstall callbacks.
- `radeon_msi_ok()`: hardware and quirk policy for enabling MSI.
- `radeon_irq_kms_init()` / `radeon_irq_kms_fini()`: top-level IRQ lifecycle, including spinlock init, vblank init, MSI enable/disable, work item setup, request_irq, and teardown flushing.
- `radeon_irq_kms_sw_irq_get*()` / `put()`: reference-count software interrupts per ring for fence signaling.
- `radeon_irq_kms_pflip_irq_get()` / `put()`: reference-count pageflip interrupts per CRTC.
- `radeon_irq_kms_enable_afmt()` / `disable_afmt()` and `enable_hpd()` / `disable_hpd()`: boolean interrupt source toggles under `rdev->irq.lock`.
- `radeon_irq_kms_set_irq_n_enabled()`: read-modify-write helper for numbered interrupt enable registers.

## Control Flow

Initialization sets up `rdev->irq.lock`, requests immediate vblank disable for power savings, initializes DRM vblank accounting for `rdev->num_crtc`, applies MSI policy, initializes deferred work, marks IRQs installed, and calls `request_irq()`. Preinstall clears all software state under the IRQ spinlock, calls the per-ASIC `radeon_irq_set()` to disable hardware interrupt sources, then processes pending bits once to clear stale status. Postinstall configures the DRM maximum vblank counter based on Avivo vs legacy width.

Runtime consumers call get/put helpers around features needing interrupt delivery. Atomic counters are used for ring software interrupts and page flips so the first user enables hardware and the last user disables it. Boolean HPD/AFMT/vblank states are updated under the same spinlock before reprogramming hardware through `radeon_irq_set()`.

The hard IRQ handler does little policy work itself: it delegates to ASIC-specific status decoding and only marks runtime PM activity on handled interrupts. HPD/DP work later walks connectors under `mode_config->mutex` to avoid doing modeset operations in IRQ context.

## State and Persistence Behavior

Persistent IRQ state lives in `rdev->irq`: `installed`, spinlock, per-ring `ring_int[]` atomics, per-CRTC `pflip[]` atomics and `crtc_vblank_int[]`, HPD booleans, AFMT booleans, and DPM thermal state. MSI state persists in `rdev->msi_enabled`. Deferred work items persist until device teardown. Hardware enable registers are reprogrammed from this state after each transition.

## Dependencies and Integration Points

This file integrates with PCI/MSI, runtime PM, DRM vblank core, DRM probe-helper hotplug events, Radeon ASIC IRQ callbacks (`radeon_irq_process`, `radeon_irq_set`), connector hotplug handling, DisplayPort link work, HDMI audio update work, fence signaling, page flipping, and per-family register programming helpers.

## Risks and Edge Cases

- MSI policy is quirk-heavy; enabling MSI on broken IGPs or disabling it on systems requiring MSI can cause missed interrupts or lockups.
- `radeon_irq_kms_disable_hpd()` uses `rdev->irq.hpd[i] &= !(mask bit)`, which works as boolean clearing but is easy to misread and fragile if the field ever becomes non-boolean.
- `radeon_irq_kms_sw_irq_get_delayed()` increments without programming hardware; callers must later call a path that applies `radeon_irq_set()`.
- `radeon_irq_kms_fini()` flushes delayed hotplug work but not the plain `dp_work` or `audio_work` here, so teardown ordering must ensure those cannot run after device state is invalid.
- All IRQ state changes depend on per-ASIC `radeon_irq_set()` honoring the software state consistently.

## Test Signals

Validation should include boot with legacy INTx and MSI, vblank enable/disable on each CRTC, pageflip completion interrupts, fence signaling on every ready ring, HPD storms and startup spurious HPD, DisplayPort hotplug work, HDMI AFMT interrupt toggles, suspend/resume IRQ reinstall, runtime PM last-busy updates, and quirk systems that require or reject MSI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_irq_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_kms.c

## Purpose

`radeon_kms.c` provides the main DRM KMS driver lifecycle and several user-facing KMS callbacks. It loads/unloads the Radeon device, handles AGP/PCIe/PX runtime-PM setup, exposes the `RADEON_INFO` ioctl ABI, creates per-file VM state on open, releases per-file resources on close, and implements vblank counter and vblank interrupt callbacks for DRM core.

## Important APIs, Types, and Functions

- `radeon_driver_load_kms()`: detects AGP/PCI/PCIe flags, optional switchable-graphics PX support, initializes device core with `radeon_device_init()`, initializes modesetting, calls ACPI methods, and configures runtime PM autosuspend for PX devices.
- `radeon_driver_unload_kms()`: wakes PX devices if needed, finalizes ACPI, modeset, and core device state, removes AGP write-combine mappings, frees AGP metadata, and clears `dev_private`.
- `radeon_info_ioctl()`: large switch over `drm_radeon_info.request` returning hardware IDs, pipe/backend/tile configuration, acceleration status, VM limits, ring readiness, clocks, firmware versions, memory usage, temperature, allowed registers, reset count, and per-file HyperZ/CMASK ownership results.
- `radeon_set_filp_rights()`: serializes single-owner per-file feature rights under `rdev->gem.mutex`.
- `radeon_driver_open_kms()`: runtime-PM gets the device, allocates `struct radeon_fpriv` for Cayman+ clients, initializes a VM when acceleration works, and maps the IB pool read-only at `RADEON_VA_IB_OFFSET`.
- `radeon_driver_postclose_kms()`: drops HyperZ/CMASK ownership, frees UVD/VCE handles, removes the VM IB-pool mapping, finalizes VM state, and releases runtime PM.
- `radeon_get_vblank_counter_kms()`: reads the hardware frame counter and adjusts it to DRM's start-of-vblank semantics using scanout position.
- `radeon_enable_vblank_kms()` / `radeon_disable_vblank_kms()`: toggle per-CRTC vblank IRQ state under `rdev->irq.lock`.

## Control Flow

Load begins with bus classification and optional AGP setup/MTRR. PX is enabled only when runtime PM is allowed, ATPX is present, the device is not IGP, and it is not Thunderbolt-attached. Device initialization is expected to fail only on fatal resource/setup errors; modeset initialization should similarly fail only on fatal display setup errors. ACPI methods run after modeset because display objects must exist. PX runtime PM is configured after successful init.

The info ioctl normalizes the user pointer, defaults to a 32-bit return value, and switches by request. Some requests first read an input value from userspace, such as CRTC object ID, HyperZ/CMASK ownership intent, ring selector, or register offset. Requests returning 64-bit values redirect the output pointer to a local `u64` and change `value_size`. At the end, the selected value buffer is copied to userspace.

Open creates per-file VM state only for Cayman and later. It maps the shared IB pool BO into the client's VM read-only and snooped so IBs allocated from that pool can be referenced by virtual address. Postclose reverses those mappings, frees media handles, and clears single-owner feature grants.

The vblank counter path compensates for Radeon hardware incrementing at vsync rather than start of vblank. It reads count, queries scanout position relative to vblank start, retries if the counter changed during sampling, and increments the returned count when currently between vblank start and vsync.

## State and Persistence Behavior

Device lifetime state includes `rdev->agp`, bus flags, PX/runtime-PM state, modeset/core initialization, ACPI state, and `dev->dev_private`. Per-file state includes `struct radeon_fpriv`, `struct radeon_vm`, HyperZ/CMASK ownership pointers, and UVD/VCE handles. The info ioctl reads persistent hardware capability/configuration state and exposes it as ABI. Vblank enable state persists in `rdev->irq.crtc_vblank_int[]`.

## Dependencies and Integration Points

This file integrates with PCI/AGP, VGA switcheroo/ATPX, runtime PM, Radeon device/modeset/ACPI initialization, GEM/TTM memory managers, command submission VM support, UVD/VCE handle tracking, DRM ioctl ABI definitions, DRM vblank core, and scanout-position helpers. It is the central bridge between DRM core callbacks and Radeon internal subsystems.

## Risks and Edge Cases

- `radeon_info_ioctl()` is ABI-sensitive: changing return values, request gating, or array sizes can break Mesa/xf86-video-ati expectations.
- Some `RADEON_INFO_*` cases intentionally report historical compatibility values, such as false acceleration for Evergreen in `ACCEL_WORKING`; these are easy to "fix" incorrectly.
- The open error path must remove partially initialized VM/BO mappings and put runtime PM exactly once.
- `radeon_driver_unload_kms()` has early branches for partially initialized devices; teardown ordering must remain valid for failed probe paths.
- Vblank count correction depends on accurate scanout position. If that query is invalid, the raw hardware counter may not satisfy DRM timing semantics.

## Test Signals

Test with successful and failing probe paths, AGP and PCIe devices, PX runtime suspend/resume, every supported `RADEON_INFO` request including user-input requests and 64-bit outputs, Mesa startup capability queries, per-client VM creation and teardown, HyperZ/CMASK ownership transfer, UVD/VCE handle cleanup, vblank counter monotonicity around vblank/vsync edges, and invalid user pointer fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_kms.h

## Purpose

`radeon_kms.h` is a small private KMS header that declares the Radeon KMS vblank callback functions implemented in `radeon_kms.c`. It lets DRM driver setup and IRQ/vblank code refer to the KMS-specific vblank counter and enable/disable hooks without exposing the broader Radeon mode header.

## Important APIs, Types, and Functions

- `u32 radeon_get_vblank_counter_kms(struct drm_crtc *crtc)`: returns a DRM-adjusted frame counter for a CRTC.
- `int radeon_enable_vblank_kms(struct drm_crtc *crtc)`: enables vblank interrupt delivery for a CRTC.
- `void radeon_disable_vblank_kms(struct drm_crtc *crtc)`: disables vblank interrupt delivery for a CRTC.
- Include guard `__RADEON_KMS_H__` prevents duplicate declaration.

## Control Flow

The header has no runtime control flow. It establishes compile-time linkage from DRM driver tables or IRQ setup code to the KMS vblank implementations. Callers pass `struct drm_crtc *`; the implementation maps that CRTC to a Radeon pipe and IRQ state.

## State and Persistence Behavior

No state is stored here. The declared functions operate on persistent DRM CRTC objects and `rdev->irq` state in the implementation.

## Dependencies and Integration Points

It assumes users already have DRM CRTC type visibility through surrounding includes. The declared functions integrate with DRM core vblank callbacks and Radeon IRQ state in `radeon_irq_kms.c`/`radeon_kms.c`.

## Risks and Edge Cases

The header is intentionally narrow. Signature drift between this header and `radeon_kms.c` would break driver callback wiring at build time. Adding broader declarations here would increase coupling with unrelated KMS internals.

## Test Signals

Build coverage is the primary test signal. Runtime validation comes from DRM vblank tests that exercise the declared functions through driver callback tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_crtc.c

## Purpose

`radeon_legacy_crtc.c` implements pre-Atom/legacy Radeon CRTC programming for modesetting. It handles framebuffer base and tiling setup, legacy timing registers, PLL programming for PPLL/P2PLL, RMX panel scaling on the first CRTC, overscan reset, DPMS sequencing, CRTC prepare/commit/disable hooks, and legacy helper registration.

## Important APIs, Types, and Functions

- `radeon_legacy_init_crtc()`: assigns CRTC2 register offset and attaches legacy DRM CRTC helper functions.
- `radeon_crtc_set_base()` / `radeon_crtc_do_set_base()`: pin scanout BOs into VRAM, compute display base, pitch, tiling offset, and format, program offset/pitch/tile registers, unpin old framebuffers, and update bandwidth.
- `radeon_set_crtc_timing()`: computes and writes horizontal/vertical total/display/sync registers, format bits, CRTC enable mask defaults, merge controls, and TV-adjusted timings.
- `radeon_set_pll()`: computes or reuses BIOS PLL dividers, handles LVDS/TV constraints, programs PPLL or P2PLL with atomic-update sequencing, and switches pixel clock source.
- `radeon_legacy_rmx_mode_set()`: configures legacy flat-panel scaler/stretch registers for full/aspect/center/off modes.
- `radeon_crtc_dpms()`: toggles CRTC display/hsync/vsync bits, vblank delivery, LUT reload, and power-management clock recomputation.
- `radeon_crtc_prepare()`, `radeon_crtc_commit()`, and `radeon_crtc_disable()`: helper lifecycle methods for safely reprogramming legacy CRTCs and unpinning disabled scanout BOs.

## Control Flow

Mode setting calls `radeon_crtc_mode_set()`, which sets the scanout base, programs timings, programs PLLs, clears overscan, applies RMX scaling for CRTC0, and resets cursor state. Prepare turns off all CRTCs before reconfiguration because some legacy hardware wedges when one CRTC is reconfigured while another runs. Commit reenables previously enabled CRTCs.

Base setting validates the framebuffer format, reserves the GEM BO, pins it into VRAM under the 27-bit legacy CRTC offset limit, reads tiling flags, computes pitch in register units, and derives the CRTC offset. Macro-tiled buffers use chipset-specific offset math; microtiled scanout logs an error. If pinning a new framebuffer fails due to old small-VRAM hardware, it may unpin the old framebuffer first and retry.

Timing setup derives sync widths and polarities from the adjusted mode, detects whether the CRTC drives TV output, writes CRTC1 or CRTC2 control bits, and lets `radeon_legacy_tv_adjust_crtc_reg()` override values for TV modes. PLL setup chooses PPLL/P2PLL by CRTC, sets legacy PLL flags based on pixel clock and encoder type, optionally uses COMBIOS LVDS dividers, lets TV helpers override PLL values, and performs register update/reset/clock-source sequencing with lock delays.

## State and Persistence Behavior

Persistent state includes pinned scanout BOs, `radeon_crtc->legacy_display_base_addr`, `crtc_offset`, enabled state, RMX/native mode fields, PLL state in `rdev->clock`, display register programming, and global PM clock decisions. BO pin counts and `vram_pin_size` persist until explicit unpin. Register state persists across modes until next modeset, DPMS, suspend/resume restore, or teardown.

## Dependencies and Integration Points

This file depends on DRM CRTC helper APIs, DRM framebuffer formats, Radeon BO/pin/tiling APIs, register macros, PM clock recomputation, bandwidth updates, cursor reset, PLL computation helpers, legacy TV helpers, encoder active-device state, and BIOS-provided LVDS private data. It is paired with `radeon_legacy_encoders.c` for output routing.

## Risks and Edge Cases

- Legacy CRTC offsets are limited to 27 bits; pinning outside that range fails, so small/fragmented VRAM paths are fragile.
- Scanout of microtiled buffers is only logged as an error after pinning; the function still proceeds.
- Register programming is heavily chipset-specific, especially R300 tiling, RS4xx enable quirks, mobility PLL avoidance, and TV path overrides.
- Busy waits around PLL atomic-update bits can hang if hardware never clears expected bits; some loops have workaround bounds, others spin until clear.
- `radeon_crtc_prepare()` globally disables all CRTCs, so incorrect enabled tracking can blank outputs after modeset.

## Test Signals

Validation should include mode set on CRTC0 and CRTC1, 8/16/24/32-bpp scanout, framebuffer panning offsets, macro-tiled and linear scanout, small VRAM old-GPU retry paths, LVDS RMX full/center/aspect/off, TV output timing/PLL adjustment, DPMS on/off and vblank state, cursor reset after modeset, suspend/resume preserving display, and lockdep/reservation tests around BO pin/unpin.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_encoders.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_encoders.c

## Purpose

`radeon_legacy_encoders.c` implements legacy output encoder handling for LVDS, primary DAC, internal TMDS, external DVO/TMDS, and TV DAC encoders. It wires DRM encoder helper callbacks, performs DPMS and mode routing through direct register programming, registers legacy LVDS backlight devices, performs analog/TV load detection, retrieves BIOS encoder private data, and creates/merges legacy encoder objects.

## Important APIs, Types, and Functions

- `radeon_add_legacy_encoder()`: creates or updates a `struct radeon_encoder`, sets possible CRTCs/devices, chooses encoder funcs/helper funcs by Atom object ID, and loads encoder-private BIOS data.
- `radeon_legacy_encoder_disable()`: calls the encoder's DPMS-off helper and clears `active_device`.
- LVDS path: `radeon_legacy_lvds_update()`, `*_dpms`, `*_prepare`, `*_commit`, `*_mode_set`, `radeon_legacy_get_backlight_level()`, `radeon_legacy_set_backlight_level()`, `radeon_legacy_backlight_init()`, and destroy helpers.
- Primary DAC path: `radeon_legacy_primary_dac_dpms()`, `*_mode_set()`, and `radeon_legacy_primary_dac_detect()`.
- Internal TMDS path: `radeon_legacy_tmds_int_dpms()` and `*_mode_set()` program `FP_GEN_CNTL`, TMDS PLL, and transmitter registers.
- External TMDS/DVO path: `radeon_legacy_tmds_ext_*()` programs `FP2_GEN_CNTL` and calls Atom/COMBIOS/external DVO setup helpers.
- TV DAC path: `radeon_legacy_tv_dac_*()`, `radeon_legacy_tv_detect()`, `r300_legacy_tv_detect()`, `radeon_legacy_ext_dac_detect()`, and `radeon_legacy_tv_dac_detect()`.
- Private-data loaders `radeon_legacy_get_tmds_info()` and `radeon_legacy_get_ext_tmds_info()` combine AtomBIOS, COMBIOS, and fallback table sources.

## Control Flow

Connector discovery calls `radeon_add_legacy_encoder()` with an encoder enum and supported device mask. If the encoder already exists, its device mask is extended; otherwise a new DRM encoder is initialized with helper functions matching the encoder ID. LVDS is limited to CRTC0 and defaults to full RMX scaling; other legacy encoders can generally drive either CRTC unless the device is single-CRTC.

During modeset, the common fixup path sets `active_device`, computes adjusted CRTC info, and applies panel mode fixup for LCDs. Prepare locks the output through AtomBIOS or COMBIOS scratch mechanisms and powers the encoder down. Mode-set functions select source CRTC/RMX, program output-specific PLL/routing/DAC registers, and update BIOS scratch CRTC routing. Commit powers the encoder on and releases the output lock for most paths.

Detection paths save the registers they need, force known DAC/TV/DVO test patterns, wait for comparator/GPIO results, then restore the saved state. TV and secondary DAC detection have separate R300, R200 external DAC, single-CRTC, and connector-type branches.

Backlight registration allocates private data, respects platform native-backlight policy, detects positive/negative brightness sense, stores the backlight device in Atom or legacy LVDS private data, initializes brightness from hardware, and updates mode-info `bl_encoder`.

## State and Persistence Behavior

Persistent state includes DRM encoder objects, `radeon_encoder` fields (`devices`, `active_device`, `rmx_type`, `enc_priv`, output CSC/audio fields), BIOS-derived private structs for LVDS/DAC/TMDS/TV, LVDS backlight device and brightness, connector routing scratch registers, and direct hardware output registers. Detection routines temporarily perturb registers and must restore them exactly.

## Dependencies and Integration Points

The file integrates with DRM encoder helpers, Linux backlight and ACPI video policy, Radeon BIOS parsers, AtomBIOS/COMBIOS output locks and scratch registers, legacy CRTC code, legacy TV mode programming, external TMDS/DVO helpers, I2C bus records for DVO chips, PMac backlight support, and connector detection flows.

## Risks and Edge Cases

- Several commit functions for internal TMDS and TV DAC call output lock with `true` after enabling, unlike other paths that unlock with `false`; this may be intentional for legacy hardware but is a high-risk semantic trap.
- Load detection temporarily rewrites many display registers. Missing restore on new early returns would corrupt active displays.
- Backlight polarity detection uses heuristics and platform exceptions; incorrect polarity inverts brightness.
- `enc_priv` is a `void *` whose concrete type depends on encoder ID and BIOS type, so wrong casts can silently corrupt behavior.
- External TMDS setup falls through multiple data sources; absent or invalid BIOS data may still create an encoder with limited private state.
- Some detection paths refuse probing while CRTC2 is in use, which can produce connector-status differences depending on active modes.

## Test Signals

Test LVDS panel power sequencing and backlight on AtomBIOS and COMBIOS systems, primary/secondary DAC load detection, TV S-video/composite detection, internal and external DVI modes, CRTC0/CRTC1 routing, RMX with LVDS/TMDS, output lock/scratch register updates, backlight registration skip under ACPI native policy, PMac backlight cases, suspend/resume encoder restore, and repeated detect while displays are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_encoders.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_encoders.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_encoders.h

## Purpose

`radeon_legacy_encoders.h` is the private declaration header for legacy Radeon encoder setup. It exposes the two functions other mode/discovery code needs: LVDS backlight registration and legacy encoder creation/merging.

## Important APIs, Types, and Functions

- `radeon_legacy_backlight_init(struct radeon_encoder *, struct drm_connector *)`: registers and initializes a legacy LVDS backlight device for the connector/encoder pair.
- `radeon_add_legacy_encoder(struct drm_device *, uint32_t encoder_enum, uint32_t supported_device)`: creates or updates a DRM/Radeon legacy encoder based on BIOS object information and supported device mask.
- Include guard `__RADEON_LEGACY_ENCODERS_H__` provides normal private-header protection.

## Control Flow

The header itself has no runtime flow. Legacy connector/BIOs discovery includes it to call `radeon_add_legacy_encoder()` as encoders are found. LVDS connector setup includes it to register backlight control after the encoder private data is available.

## State and Persistence Behavior

No state is stored here. The declared functions allocate/update DRM encoder objects, Radeon encoder private data, and backlight devices in `radeon_legacy_encoders.c`.

## Dependencies and Integration Points

The declarations rely on `struct radeon_encoder`, `struct drm_connector`, and `struct drm_device` being visible through including contexts. It is part of the private display subsystem contract alongside `radeon_mode.h`.

## Risks and Edge Cases

Because this header is narrow, its main risk is signature drift from the implementation or callers. Adding broad legacy display declarations here would increase coupling and make the legacy modeset boundary harder to maintain.

## Test Signals

Build coverage for legacy connector discovery and LVDS backlight setup is the main signal. Runtime coverage comes from successful encoder creation and backlight registration on legacy Radeon systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_encoders.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_tv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_tv.c

## Purpose

`radeon_legacy_tv.c` programs the integrated legacy TV-out block. It contains NTSC/PAL timing constants, TV PLL settings, horizontal/vertical code timing tables, restart/position/size calculations, FIFO writes for timing microcode, full TV mode programming, and helper hooks that let legacy CRTC PLL/timing setup use TV-specific values.

## Important APIs, Types, and Functions

- `struct radeon_tv_mode_constants`: captures per-standard/per-reference-clock CRTC and TV timing values.
- `available_tv_modes[]`, `hor_timing_NTSC/PAL[]`, and `vert_timing_NTSC/PAL[]`: hard-coded timing presets for 800x600 TV output.
- `radeon_legacy_tv_get_std_mode()`: selects NTSC/PAL and 27 MHz/14 MHz constants based on TV standard and active CRTC PLL reference.
- `radeon_wait_pll_lock()`: polls PLL test counters after TV PLL programming.
- `radeon_legacy_tv_write_fifo()`, `radeon_get_htiming_tables_addr()`, `radeon_get_vtiming_tables_addr()`, and `radeon_restore_tv_timing_tables()`: write horizontal/vertical TV timing code tables into the hardware FIFO.
- `radeon_legacy_tv_init_restarts()` and `radeon_legacy_write_tv_restarts()`: compute and program frame/vertical/horizontal restart positions from user TV position/size controls.
- `radeon_legacy_tv_mode_set()`: full TV block programming sequence, including master control, DAC, TV PLL, scaler/filter/modulator registers, timing tables, restart registers, and gain settings.
- `radeon_legacy_tv_adjust_crtc_reg()`, `radeon_legacy_tv_adjust_pll1()`, and `radeon_legacy_tv_adjust_pll2()`: adjust CRTC timing and PLL parameters for TV output.

## Control Flow

TV mode setting starts by selecting a standard mode based on the encoder's `tv_std` and active CRTC PLL reference. It computes master control, modulator levels, RGB source selection, vertical scaler increments, flicker-removal filter parameters, TV timing control, DAC standard/adjustment bits, and TV PLL dividers. It copies standard timing code arrays into the encoder's persistent `tv` cache, computes restart values and horizontal-size increments, then programs hardware in a reset-oriented sequence: assert TV/CRT/FIFO resets, power down DAC blanking, program and lock TV PLL, program HV/scaler/filter registers, write restarts, restore timing tables via FIFO, program standard/modulator/pre-DAC/gain registers, and finally enable the TV master/DAC.

The CRTC helpers are called from `radeon_legacy_crtc.c` when a CRTC is driving TV output. They override horizontal/vertical CRTC totals and sync starts to match the selected TV mode, and they replace PPLL/P2PLL divider values and pixel-clock source bits with the TV-specific values.

## State and Persistence Behavior

Persistent per-encoder TV state lives in `struct radeon_encoder_tv_dac`: selected standard, supported standards, user h/v position and h size, adjustment values, and cached `struct radeon_tv_regs` timing/restart tables. Hardware state persists in TV master, PLL, scaler, DAC, modulator, FIFO timing, restart, and gain registers until another TV modeset or suspend/resume restore.

## Dependencies and Integration Points

This file depends on Radeon register macros, `struct radeon_encoder_tv_dac` and TV standard enums from `radeon_mode.h`, active CRTC state, legacy encoder TV DAC setup, and legacy CRTC timing/PLL programming. It is invoked only through the legacy TV DAC path in `radeon_legacy_encoders.c` and the TV adjustment hooks in `radeon_legacy_crtc.c`.

## Risks and Edge Cases

- Timing tables and magic constants are hardware-specific; small arithmetic or table changes can break analog TV output.
- FIFO write acknowledgement loops have finite counters but no explicit failure reporting, so programming failure can be silent.
- `radeon_legacy_tv_init_restarts()` uses signed arithmetic and casts back to unsigned fields; extreme position/size values need clamping by callers/properties.
- `SLOPE_limit` lookup assumes flicker-removal values fall within the table; if not, index `i` can reach `ARRAY_SIZE(SLOPE_limit)` and then index adjacent arrays out of bounds.
- Only a small fixed mode set is represented here, centered on 800x600 constants.
- TV PLL lock polling is heuristic and may be sensitive to reference-clock or silicon differences.

## Test Signals

Hardware validation should cover NTSC, NTSC-J, PAL, PAL-M, PAL-60, SCART PAL where supported, both 27 MHz and 14 MHz references, CRTC0 and CRTC1 TV routing, h/v position and h-size property changes, composite and S-video outputs, suspend/resume, repeated modesets, PLL lock stability, and visual timing checks for overscan/flicker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_tv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_mn.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_mn.c

## Purpose

`radeon_mn.c` connects Radeon userptr buffer objects to the Linux MMU interval-notifier API. It registers notifiers for user-backed BO address ranges, invalidates GPU bindings when the CPU page tables change, waits for outstanding GPU use, migrates affected BOs back to CPU/system placement, and unregisters notifiers during BO cleanup.

## Important APIs, Types, and Functions

- `radeon_mn_invalidate()`: MMU interval invalidation callback for one BO. It checks whether the BO has a bound TTM TT, rejects non-blockable invalidations by returning `false`, reserves the BO, waits on its reservation object, changes placement to `RADEON_GEM_DOMAIN_CPU`, validates/migrates it through TTM, and unreserves it.
- `radeon_mn_ops`: `mmu_interval_notifier_ops` table pointing at the invalidate callback.
- `radeon_mn_register(struct radeon_bo *bo, unsigned long addr)`: inserts the interval notifier for `current->mm`, the user address, and `radeon_bo_size(bo)`, then starts an interval read sequence.
- `radeon_mn_unregister(struct radeon_bo *bo)`: removes the notifier if registered and clears `bo->notifier.mm`.

## Control Flow

Registration is called when a Radeon BO wraps user memory. The notifier watches the user virtual range in the current process. When the MM subsystem invalidates that range, the callback first ignores BOs that are not bound into GPU-visible TT memory. If the invalidation cannot block, it returns `false` so the MMU notifier core can retry in a blockable context. In blockable mode it reserves the BO, waits indefinitely for bookkeeping usage on the reservation object, switches allowed placement to CPU, validates the TTM BO to unbind/move it, logs errors, unreserves, and returns `true`.

Unregister is idempotent and does nothing when no `mm` is recorded. After removal it clears the pointer to prevent duplicate unregister attempts.

## State and Persistence Behavior

The persistent state is the `mmu_interval_notifier` embedded in `struct radeon_bo` and the BO's TTM placement/binding. Invalidation may persistently move the BO out of GPU/GTT placement into CPU/system memory. Reservation fences and waits coordinate with in-flight GPU work before CPU page-table changes are allowed to proceed.

## Dependencies and Integration Points

This file depends on Linux `mmu_interval_notifier`, TTM BO validation, Radeon BO reserve/unreserve and placement helpers, Radeon TTM userptr binding checks, DMA reservation waits, and current process `mm`. It is integrated with GEM userptr BO creation and cleanup.

## Risks and Edge Cases

- The source contains an explicit FIXME: Radeon appears to allow `get_user_pages` during invalidate start/end and should use the full `mmu_interval_read_begin()` scheme around GUP reads for safe PTE sampling.
- Invalidation waits with `MAX_SCHEDULE_TIMEOUT`; stuck GPU work or reservation misuse can stall mm invalidation.
- Errors during reserve, wait, or validate are logged but the callback generally returns `true`, so the MM path may continue after a failed migration.
- Registration uses `current->mm`; callers must ensure this is the owning mm for the userptr range.
- Non-blockable invalidations rely on the core retrying later; incorrect caller assumptions can cause missed unbinding.

## Test Signals

Test with userptr BOs under munmap, mremap, fork/exit, swap, memory pressure, and concurrent GPU access; invalidation from blockable and non-blockable paths; forced TTM validation failure; BO cleanup idempotent unregister; lockdep coverage for reservation inside mmu notifier callbacks; and stress tests for userptr command submission while CPU mappings change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_mn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_mode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_mode.h

## Purpose

`radeon_mode.h` is the central private display-mode contract for the Radeon DRM driver. It defines display constants, GPIO/I2C bus records, PLL data, connector/encoder/CRTC state structures, TV/backlight/DisplayPort/AtomBIOS helper structures, scanout-position flags, and a large set of cross-file declarations for connector discovery, encoder programming, CRTC modesetting, I2C, DP AUX, BIOS parsing, PLL computation, fbdev, hotplug, and flip handling.

## Important APIs, Types, and Definitions

- Conversion macros `to_radeon_crtc`, `to_radeon_connector`, and `to_radeon_encoder` map DRM base objects to Radeon wrappers.
- Limits: `RADEON_MAX_HPD_PINS`, `RADEON_MAX_CRTCS`, `RADEON_MAX_AFMT_BLOCKS`, `RADEON_MAX_I2C_BUS`, `RADEON_MAX_BL_LEVEL`, and TV timing array lengths.
- Enums for RMX scaling, TV standards, underscan policy, HPD IDs, output CSC, connector audio, connector dithering, DVO chips, and page-flip status.
- `struct radeon_i2c_bus_rec` and `struct radeon_i2c_chan`: describe GPIO/hardware/AUX I2C buses and live Linux I2C adapters.
- `struct radeon_pll`, `struct atom_clock_dividers`, `struct atom_mpll_param`, and memory/voltage table structs: carry PLL and firmware-table values across AtomBIOS/display/power code.
- `struct radeon_mode_info`: persistent display subsystem state, connector table kind, CRTC/AFMT arrays, DRM properties, hardcoded EDID, firmware flags, active encoders, and backlight encoder.
- `struct radeon_crtc`: wraps `drm_crtc` with legacy offset, cursor state, RMX/native mode, PLL sharing, page flip work/status, DPM watermarks, current encoder/connector, output CSC, and scanout mode.
- Encoder-private structs for primary DAC, LVDS, TV DAC, internal/external TMDS, Atom DIG, and Atom DAC.
- `struct radeon_encoder`, `struct radeon_connector_atom_dig`, `struct radeon_hpd`, `struct radeon_router`, and `struct radeon_connector`: persistent routing, HPD, DDC, router, EDID, audio/dither, and encoder metadata.
- Function declarations cover Atom and legacy connector/encoder discovery, I2C/DDC, DP, PLL computation, CRTC base/mode/cursor handling, BIOS scratch registers, framebuffer init, fbdev, TV adjustment, FMT blocks, vblank/flip handling, and DIG encoder allocation.

## Control Flow

The header has no executable flow, but it defines the object model used by the display stack. BIOS discovery fills `radeon_mode_info`, creates connectors/encoders using the declared add/link functions, and populates I2C/HPD/router records. Modeset paths use `radeon_crtc`, `radeon_encoder`, and `radeon_connector` fields to choose PLLs, route sources, program encoders, validate scaling, and handle DP link training. Hotplug, DDC, and AUX flows use the connector's HPD/router/I2C state. Page flip and vblank handling use CRTC flip status/work and scanout helpers.

## State and Persistence Behavior

Almost every structure here is persistent for at least a DRM object lifetime. Mode info persists for the device, connectors and encoders persist through modeset teardown, CRTC state tracks current scanout/cursor/flip/PLL information, and encoder-private data stores BIOS-derived panel/DAC/TV/TMDS parameters. Some fields cache user properties such as underscan, dither, audio, TV standard, and output CSC. Firmware table structs are parsed snapshots of AtomBIOS data used by display and power management.

## Dependencies and Integration Points

This header depends on DRM CRTC/encoder/modeset helper types, DP helper definitions, Linux I2C and bit-bang I2C, fixed-point math, Radeon BO forward declarations, AtomBIOS object IDs and encoder modes through included Radeon headers, and many implementation files under `drivers/gpu/drm/radeon`. It is included by legacy and Atom display files, connector code, DP/AUX code, framebuffer code, IRQ/KMS vblank code, and BIOS parser code.

## Risks and Edge Cases

- This is a high-coupling private ABI: changing struct fields, enum values, or prototypes can ripple across many Radeon display files.
- `void *enc_priv` and connector private pointers require correct type discipline by encoder/connector kind.
- Several structs mix persistent state, cached hardware values, and user properties; stale values can cause incorrect resume, hotplug, or modeset behavior.
- Bitfield layouts in Atom divider structs are endian-sensitive and must match firmware expectations.
- Limit constants must match hardware and array sizes used in IRQ, CRTC, AFMT, I2C, and timing code.

## Test Signals

Build coverage across the Radeon display subsystem is mandatory. Runtime signals include connector discovery on AtomBIOS and COMBIOS boards, DP/DVI/VGA/LVDS/TV modesets, I2C/DDC/AUX probing, HPD routing, page flips, vblank accounting, cursor operations, backlight properties, TV/underscan/audio/dither/output-CSC properties, suspend/resume, and 32-bit/big-endian builds for bitfield layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_object.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_object.c

## Purpose

`radeon_object.c` implements Radeon GEM/TTM buffer-object management. It creates and destroys BOs, maps/unmaps them for the kernel, handles references, pins/unpins BOs into VRAM/GTT, initializes/finalizes TTM memory management, validates command-submission BO lists, manages legacy surface registers for tiled CPU mappings, responds to BO moves and CPU faults, evicts VRAM, force-deletes leaked objects, and attaches Radeon fences to DMA reservations.

## Important APIs, Types, and Functions

- `radeon_ttm_bo_destroy()` and `radeon_ttm_bo_is_radeon_bo()`: Radeon TTM object destructor and type predicate.
- `radeon_ttm_placement_from_domain()`: converts Radeon GEM domains and flags into TTM placement arrays, including visible-VRAM constraints for CPU-accessible BOs and invisible-VRAM preference for no-CPU-access BOs.
- `radeon_bo_create()`: aligns size, chooses TTM BO type, initializes GEM object, applies architecture/chipset cacheability restrictions, initializes placement, and calls `ttm_bo_init_validate()`.
- `radeon_bo_kmap()` / `radeon_bo_kunmap()`: wait for kernel usage, map/unmap BO pages through TTM, cache `bo->kptr`, and update tiling surface state.
- `radeon_bo_ref()` / `radeon_bo_unref()`: GEM reference wrappers.
- `radeon_bo_pin_restricted()`, `radeon_bo_pin()`, and `radeon_bo_unpin()`: validate BO placement, disallow userptr pinning, account pinned VRAM/GART sizes, and return GPU offsets.
- `radeon_bo_evict_vram()`, `radeon_bo_force_delete()`, `radeon_bo_init()`, and `radeon_bo_fini()`: memory-manager lifecycle and emergency cleanup.
- `radeon_bo_list_validate()`: reserve all BOs for command submission, migrate them to preferred/allowed domains within a bytes-moved threshold, handle UVD segment constraints, and record GPU offsets/tiling flags.
- `radeon_bo_get_surface_reg()`, `radeon_bo_clear_surface_reg()`, `radeon_bo_set_tiling_flags()`, `radeon_bo_get_tiling_flags()`, and `radeon_bo_check_tiling()`: manage legacy surface registers needed for tiled BO mappings.
- `radeon_bo_move_notify()` and `radeon_bo_fault_reserve_notify()`: TTM callbacks for move invalidation and CPU fault migration into visible VRAM/GTT.
- `radeon_bo_fence()`: reserves one DMA fence slot and records shared/exclusive Radeon fences on the BO reservation object.

## Control Flow

BO creation initializes the wrapper, embeds the GEM object, strips unsupported cache flags based on bus, ASIC, architecture, and PAT/WC support, computes initial placement from requested domains, takes the memory-clock read lock, and asks TTM to allocate/validate the BO. Destruction removes the BO from the GEM object list under `gem.mutex`, clears any surface register, warns on leftover VM mappings, destroys PRIME import state if present, releases the GEM object, and frees the wrapper.

Pinning requires the caller to hold reservation. Userptr BOs cannot be pinned. Already-pinned BOs just increment TTM pin count and return current GPU address. First pin validates the BO into the requested domain and optional max offset, constraining CPU-accessible VRAM pins to visible VRAM when needed, then pins and updates aggregate pin accounting.

Command submission validation first uses `drm_exec` to reserve every BO. It then iterates the list, skips pinned BOs, chooses preferred placement but avoids excessive relocations after a dynamic VRAM-usage threshold, validates with TTM, retries with allowed domains on non-signal failures, applies UVD segment restrictions when needed, and records GPU offset and tiling flags for relocation emission.

Surface-register management is demand-driven for BOs with `RADEON_TILING_SURFACE`. It reuses existing surface registers, finds free entries, or steals one from an unpinned BO by unmapping that BO's CPU virtual mapping. BO moves and force-drop paths clear surface state and invalidate VM mappings.

CPU faults on invisible VRAM try to migrate the BO into visible VRAM; if that fails with `-ENOMEM`, the path falls back to GTT. Pinned invisible BOs fault with SIGBUS because they cannot be moved.

## State and Persistence Behavior

Persistent BO state includes GEM/TTM object state, placement arrays, flags, initial domain, tiling flags/pitch, surface register index, kernel mapping pointer, VM mapping list, PRIME import attachment, reservation fences, and pin counts. Device-level state includes GEM object list, aggregate VRAM/GART pinned sizes, TTM managers, VRAM WC/MTRR reservations, surface-register ownership, and atomic bytes-moved counters.

## Dependencies and Integration Points

This file depends on DRM GEM, DRM PRIME, DMA reservation/fence APIs, TTM resource managers and BO validation, architecture WC/MTRR helpers, Radeon TTM backend, Radeon tracing, VM invalidation, UVD placement constraints, command submission BO lists, and legacy surface-register hardware callbacks. It is a core dependency for framebuffer scanout, command submission, cursor BOs, IB pools, user GEM objects, and PRIME sharing.

## Risks and Edge Cases

- `radeon_bo_create()` leaks the allocated wrapper if `ttm_bo_init_validate()` fails before the TTM destructor owns it; ownership should be checked against the TTM API version in this tree.
- BO reservation discipline is critical. Several functions assert or assume the BO reservation is held; callers that skip reservation can race placement/tiling/pin state.
- Surface-register stealing unmaps another BO's virtual mappings and relies on unpinned selection; bugs can disturb CPU mappings unexpectedly.
- Pin accounting must exactly match first pin and final unpin or memory pressure reporting becomes wrong.
- Userptr, PRIME-shared, and no-CPU-access flags impose placement restrictions that can be violated by future call paths.
- Fault migration from invisible VRAM can fail with SIGBUS for pinned BOs, which is correct but user-visible.

## Test Signals

Test BO creation across VRAM/GTT/CPU domains, cache flag variants, PRIME imports, userptr rejection on pin, kmap/kunmap, pin/unpin accounting, visible-VRAM constraints, command submission validation under memory pressure, bytes-moved threshold behavior, UVD segment placement, tiling flag validation for Evergreen+, surface-register allocation/steal/clear, CPU faults on invisible VRAM, VRAM eviction, forced object delete diagnostics, and fence attachment under OOM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_object.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_object.h

## Purpose

`radeon_object.h` is the private public-facing header for Radeon BO and suballocation helpers. It defines inline domain/reservation/address helpers, declares the BO lifecycle/pinning/tiling/fencing APIs implemented in `radeon_object.c`, and declares suballocator manager functions used by IB and scratch allocation code.

## Important APIs, Types, and Functions

- `radeon_mem_type_to_domain(u32 mem_type)`: maps TTM memory placement types to Radeon GEM domains.
- `radeon_bo_reserve()` / `radeon_bo_unreserve()`: wrappers around TTM reservation with Radeon logging and signal behavior controlled by `no_intr`.
- `radeon_bo_gpu_offset()`: computes GPU address from TTM resource start plus VRAM or GTT aperture base.
- `radeon_bo_size()`, `radeon_bo_ngpu_pages()`, `radeon_bo_gpu_page_alignment()`, and `radeon_bo_mmap_offset()`: inline BO size/page/mmap queries.
- Extern BO APIs: create, kmap/kunmap, ref/unref, pin/unpin, evict/fini/init, list validation, tiling get/set/check, move/fault notifications, surface register acquisition, and fence insertion.
- Suballocation helpers `to_radeon_sa_manager()`, `radeon_sa_bo_gpu_addr()`, and `radeon_sa_bo_cpu_addr()`: convert DRM suballoc manager/objects into Radeon manager and CPU/GPU addresses.
- Extern suballocation APIs: manager init/start/suspend/fini, allocate/free, and debugfs dump.

## Control Flow

The inline helpers are called throughout command submission, modesetting, VM, and memory management. Reservation wrappers are typically the first step before mutating BO placement, pinning, or tiling state. GPU offset helpers are used after validation/pinning to populate relocations, scanout registers, and IB addresses. Suballocation address helpers convert an allocated offset inside a manager BO into CPU/GPU pointers for IB emission.

## State and Persistence Behavior

The header stores no state, but all helpers operate on persistent `struct radeon_bo`, `struct ttm_buffer_object`, `struct radeon_device`, and `struct radeon_sa_manager` state. `radeon_bo_reserve()` changes reservation ownership, `radeon_bo_gpu_offset()` reflects current placement, and suballocation helpers depend on manager base CPU/GPU addresses remaining valid.

## Dependencies and Integration Points

It includes Radeon core definitions and DRM UAPI domain constants, and it depends on TTM placement/resource fields, DRM VMA node helpers, DRM suballocator APIs, and Radeon memory-controller aperture bases. Consumers include GEM ioctl paths, KMS scanout, IB allocation, command submission validation, VM updates, TTM callbacks, and debugfs.

## Risks and Edge Cases

- `radeon_bo_gpu_offset()` assumes the BO has a valid TTM resource and is reserved or pinned enough to keep placement stable.
- `radeon_bo_reserve()` uses inverted interruptibility (`!no_intr`) for TTM and returns `-ERESTARTSYS` when interruptible waits are signaled; callers must unwind all reservations.
- GPU page alignment divides by Radeon GPU page size after converting TTM page alignment; mismatched page-size assumptions can affect VM mappings.
- Suballocation address helpers assume the suballoc belongs to a `radeon_sa_manager`; passing another manager type would corrupt container lookup.

## Test Signals

Build coverage across BO users catches signature drift. Runtime signals include reservation/unreservation under contention and signal interruption, correct GPU offsets in VRAM and GTT, mmap offsets for GEM handles, VM page-count/alignment calculations, IB suballocation CPU/GPU addresses, and debugfs suballocator dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_object.h -->
