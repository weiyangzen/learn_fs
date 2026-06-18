# Research Report: subset-b-005814

This grouped report covers the requested DRM, Intel display, TTM, and device-tree binding headers. Each source file section is bounded by the reconciliation markers used by the research guard.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/gud.h -->
# sources/distributed-fs/ceph-client/include/drm/gud.h

Purpose: defines the public USB Generic Display protocol ABI shared by host and device firmware. It is entirely packed wire data and request/status constants, covering descriptor discovery, modes, connectors, properties, framebuffer transfers, state validation, and DPMS/controller enablement.

Important APIs/types/functions: `gud_display_descriptor_req`, `gud_property_req`, `gud_display_mode_req`, `gud_connector_descriptor_req`, `gud_set_buffer_req`, and variable-length `gud_state_req` are the exported protocol records. Constants cover display magic, protocol flags such as `GUD_DISPLAY_FLAG_STATUS_ON_SET` and `GUD_DISPLAY_FLAG_FULL_UPDATE`, LZ4 compression, connector types, mode flags compatible with DRM/RandR, TV/backlight/rotation properties, USB request numbers, pixel formats, connector status, EDID and mode limits, and status/error codes.

Control flow: consumers first fetch the descriptor, formats, properties, connector descriptors, connector properties, status, and modes/EDID. Runtime flow validates a full `gud_state_req` with `GUD_REQ_SET_STATE_CHECK`, commits with `GUD_REQ_SET_STATE_COMMIT`, and sends damage rectangles through `GUD_REQ_SET_BUFFER` followed by bulk data unless full-update mode suppresses per-transfer setup.

State and persistence: the header persists no kernel state, but its structures define device-visible state. The full display state is resent on each change; connector changed bits and status requests are explicit protocol synchronization points.

Dependencies and integration: depends only on Linux fixed-width types and packed layout. Integrated by DRM GUD host/gadget code and USB control/bulk transports.

Risks and test signals: ABI drift, endian mistakes, non-packed layout changes, invalid flexible-array sizing, and compression/full-update incompatibility are primary risks. Tests should validate descriptor parsing, unsupported status paths, connector hotplug semantics, mode flag masks, EDID length bounds, buffer rectangle bounds, and byte-exact protocol records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/gud.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/display_member.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/display_member.h

Purpose: provides a compile-time contract that Intel parent driver structs place their `struct drm_device` member and `struct intel_display *` member at matching relative offsets. This lets shared display code recover the display pointer without needing concrete i915 or xe private struct definitions.

Important APIs/types/functions: `struct __intel_generic_device` is the reference layout with `drm` followed by `display`. `INTEL_DISPLAY_MEMBER_STATIC_ASSERT(type, drm_member, display_member)` compares the reference offset delta with a target struct's delta using `offsetof`, `static_assert`, and `__stringify`.

Control flow: no runtime control flow. The macro runs during compilation of drivers that include it and fails the build when the layout contract is violated.

State and persistence: no runtime state. The only persisted behavior is a build-time ABI-like invariant between Intel display and parent device structures.

Dependencies and integration: depends on `linux/build_bug.h`, `stddef.h`, `stringify.h`, and DRM device definitions. Used by Intel i915/xe display integration where the same display library must operate with multiple parent devices.

Risks and test signals: the main risk is a parent struct refactor that moves only one member and silently breaks pointer derivation if the assertion is absent. Build coverage for both i915 and xe private structs is the key test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/display_member.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/display_parent_interface.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/display_parent_interface.h

Purpose: defines the service table that an Intel parent/core graphics driver provides to the shared display driver. It decouples display code from i915/xe internals by grouping callbacks for buffer objects, DPT, DSB, frontbuffer, HDCP GSC, initial planes, IRQs, overlay, panic scanout, PC8, pcode, runtime PM, RPS, stolen memory, and VMAs.

Important APIs/types/functions: `struct intel_display_parent_interface` is the aggregate. Subinterfaces include `intel_display_bo_interface` for GEM/FB/mmapping/key/read/describe hooks, `intel_display_dpt_interface`, `intel_display_dsb_interface`, `intel_display_frontbuffer_interface`, `intel_display_hdcp_interface`, `intel_display_initial_plane_interface`, `intel_display_irq_interface`, `intel_display_overlay_interface`, `intel_display_panic_interface`, `intel_display_pc8_interface`, `intel_display_pcode_interface`, `intel_display_rpm_interface`, `intel_display_rps_interface`, `intel_display_stolen_interface`, and `intel_display_vma_interface`.

Control flow: display probe receives this table, then calls parent callbacks at display lifecycle points: framebuffer lookup/init/fini, DSB buffer creation and writes, HDCP GSC messaging, initial plane allocation/setup, IRQ synchronization, runtime-PM wakeref acquire/release, pcode mailbox requests, stolen memory node allocation, and overlay transitions. Non-optional callbacks must be callable without NULL checks.

State and persistence: no state is stored in the header, but callback ownership covers persistent parent state such as GEM objects, stolen allocations, RPM wakerefs, DSB buffers, HDCP GSC contexts, and frontbuffer references. Lifetime and locking are delegated to the parent.

Dependencies and integration: forward declares DRM, GEM, fence, seq_file, VM, Intel display, VMA, DPT, DSB, HDCP, panic, stolen, and ref-tracker types. It is a central integration boundary between shared Intel display code and concrete parent drivers.

Risks and test signals: risks include incomplete tables, incorrect optional/non-optional assumptions, lifetime mismatches, RPM leaks, stale stolen node ownership, and ABI expansion without updating all parents. Test through display probe on every parent, framebuffer mmap/init, modeset paths, runtime suspend/resume, HDCP, panic scanout, and pcode error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/display_parent_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/i915_component.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/i915_component.h

Purpose: declares component binding identifiers used between i915 and companion drivers such as HDA audio, HDCP, PXP, GSC proxy, and Intel late-binding services.

Important APIs/types/functions: `enum i915_component_type` assigns component IDs: audio, HDCP, PXP, GSC proxy, and late binding. `MAX_PORTS` is the i915/display port count contract for audio state. `struct i915_audio_component` embeds `struct drm_audio_component` and stores `aud_sample_rate[MAX_PORTS]`.

Control flow: no executable flow. Component framework participants use the enum to bind matching providers/consumers; HDA uses the audio component base and per-port sample-rate array.

State and persistence: the only mutable state described here is per-port audio sample rate inside the component object. It is runtime state owned by the component provider/consumer, not persisted by this header.

Dependencies and integration: depends on `drm_audio_component.h`. Integrated by i915 display audio code and audio drivers that need direct graphics/audio coordination.

Risks and test signals: `MAX_PORTS` must remain synchronized with i915's port definitions. Component ID changes are ABI-like within kernel component matching. Test audio binding, hotplug, sample-rate updates for all ports, and build coverage for every component user.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/i915_component.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/i915_drm.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/i915_drm.h

Purpose: exposes legacy i915 kernel-facing declarations and PCI config register constants related to integrated graphics stolen memory, GTT aperture sizing, VGA disable, TSEG sizing, and old IPS/GPU turbo hooks.

Important APIs/types/functions: declares `i915_read_mch_val()`, `i915_gpu_raise()`, `i915_gpu_lower()`, `i915_gpu_busy()`, and `i915_gpu_turbo_disable()`. Exports `intel_graphics_stolen_res`. Defines GMCH control offsets and masks for Sandy Bridge/Broadwell style `SNB_GMCH_CTRL`, older `I830_GMCH_CTRL`, DRB/TOUD/ESMRAMC/TSEG registers, `INTEL_BSM`, Gen11 BSM dwords, and `INTEL_BSM_MASK`.

Control flow: consuming platform/quirk/GTT code reads PCI config registers, extracts bitfields, maps stolen memory and aperture ranges, and coordinates IPS/turbo policy through the declared helper functions.

State and persistence: no local state. Hardware config registers and `intel_graphics_stolen_res` represent boot-discovered memory reservations that persist for the device lifetime.

Dependencies and integration: depends on Linux fixed-width types and `struct resource` from included kernel headers. Used by i915, intel-gtt, early quirks, and platform power management paths.

Risks and test signals: bitfield errors can mis-size stolen memory or corrupt reserved ranges. Test signals include boot logs for stolen memory detection across old and new chipsets, PCI config decoding, VGA disable handling, and no overlap with system RAM resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/i915_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/i915_gsc_proxy_mei_interface.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/i915_gsc_proxy_mei_interface.h

Purpose: defines the component interface between i915 and MEI drivers for forwarding GSC proxy messages between graphics firmware and management engine firmware.

Important APIs/types/functions: `struct i915_gsc_proxy_component_ops` holds an owning module plus `send()` and `recv()` callbacks. `struct i915_gsc_proxy_component` stores the MEI device pointer and ops table.

Control flow: i915 obtains the component, calls `send(dev, buf, size)` to transmit GSC-originated proxy data to ME firmware, and calls `recv(dev, buf, size)` to collect the ME response. Return values are byte counts or negative errno.

State and persistence: state is limited to the bound MEI device and stable ops pointer. Buffers are caller-managed transient payloads.

Dependencies and integration: depends on Linux types plus forward-declared `device` and `module`. Integrated through the component framework and MEI service drivers.

Risks and test signals: risks include short transfers, stale device/ops after unbind, module lifetime mistakes, and mismatched message sizes. Test component bind/unbind, send/recv failure paths, firmware timeout handling, and concurrent proxy traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/i915_gsc_proxy_mei_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/i915_hdcp_interface.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/i915_hdcp_interface.h

Purpose: defines Intel's HDCP 2.x service interface and the packed HECI/GSC firmware command ABI used by i915, MEI HDCP, and GSC HDCP implementations.

Important APIs/types/functions: enumerations define port type, wired protocol, DDI identifiers, transcoder identifiers, firmware status codes, and HDCP command IDs. `struct hdcp_port_data` carries port/transcoder/protocol, stream count, sequence number, and MST stream list. `struct i915_hdcp_ops` exposes the full authentication flow: initiate session, verify receiver cert and H', store pairing, locality check, session key, repeater topology, M', enable authentication, and close session. `struct i915_hdcp_arbiter` binds device, ops, and mutex. Packed command structs model every HECI request/response, including headers, port IDs, AKE, LC, SKE, repeater, and stream-management payloads.

Control flow: display HDCP code maps connector state into `hdcp_port_data`, calls ops in HDCP protocol order, and the provider serializes firmware commands using the packed structures and buffer-length constants. Repeater/MST paths update `seq_num_m` and stream arrays.

State and persistence: persistent runtime state lives in the arbiter and service device binding. HDCP sessions are firmware-side per port; pairing info and authentication state are established and closed by commands.

Dependencies and integration: depends on mutex/device/module support and DRM HDCP protocol structures. Integrated by Intel display, MEI, GSC, DP/HDMI HDCP, and MST stream management.

Risks and test signals: command packing, endian fields, buffer sizes, status translation, module lifetime, and mutex coverage are critical. Test with HDCP 2.2 HDMI/DP, repeater topology, MST streams, firmware error statuses, session close on disconnect, and ABI size checks for packed messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/i915_hdcp_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/i915_pxp_tee_interface.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/i915_pxp_tee_interface.h

Purpose: declares the i915-to-TEE/GSC component interface for Protected Xe Path services.

Important APIs/types/functions: `struct i915_pxp_component_ops` contains module ownership plus `send()`, `recv()`, and `gsc_command()` callbacks. `send` and `recv` transfer opaque messages with timeouts. `gsc_command` sends a client/fence identified GSC command using input and output scatterlists. `struct i915_pxp_component` stores `tee_dev`, ops, and a mutex protecting them.

Control flow: i915 binds the component, serializes access with the mutex, sends PXP messages to the TEE device, receives replies, or submits scatter-gather GSC commands for protected content operations.

State and persistence: component state is the bound TEE device and ops table. PXP sessions and fences are maintained by provider firmware/driver state outside this header.

Dependencies and integration: depends on kernel device and mutex APIs and forward-declared `scatterlist`. Integrated by i915 PXP, TEE bus providers, and GSC command clients.

Risks and test signals: risks include timeout behavior, scatterlist sizing, stale component binding, and missing mutex discipline. Test bind/unbind, protected session setup/teardown, send/recv timeout and errno paths, and GSC command fence handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/i915_pxp_tee_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/intel-gtt.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/intel-gtt.h

Purpose: provides the shared intel-gtt/i915 interface for GMCH GTT probing, aperture discovery, entry insertion, flushing, and removal on older Intel integrated graphics.

Important APIs/types/functions: functions include `intel_gmch_gtt_get()`, `intel_gmch_probe()`, `intel_gmch_remove()`, `intel_gmch_enable_gtt()`, `intel_gmch_gtt_flush()`, page and SG insertion, range clearing, and entry reading. Constants define AGP memory types and a GFDT cached user-memory flag.

Control flow: probe initializes GMCH GTT using bridge/GPU PCI devices and AGP bridge data. Drivers query total/mappable aperture, enable GTT, insert DMA pages or scatterlist entries at page indices, flush hardware, clear ranges, and read entries for diagnostics.

State and persistence: GTT tables are persistent hardware state for the device lifetime. This header owns no memory itself but exposes operations that mutate the aperture translation table.

Dependencies and integration: depends on PCI, AGP bridge, scatter-gather, DMA, and resource types. Used by `intel-gtt.ko`, i915, and legacy AGP/GEM memory paths.

Risks and test signals: off-by-one page indices, missing flushes, wrong flags, and stale entries can corrupt GPU memory access. Test probe/remove, aperture size reporting, SG insertion, clear/readback consistency, and suspend/resume GTT restoration on legacy platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/intel-gtt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/intel_gmd_interrupt_regs.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/intel_gmd_interrupt_regs.h

Purpose: centralizes Intel graphics/display interrupt MMIO register offsets and bit definitions for legacy i915 interrupt sources, Gen8 master IRQ, Gen11 GU/GFX master IRQ, and selected Valleyview/Cherryview registers.

Important APIs/types/functions: defines interrupt source bits for PM, ISP, LPE pipes, MIPI, port, pipe vblank/event/hblank/DPBM, overlay/plane flips, errors, sync, debug, user, ASLE, and BSD. MMIO macros cover `GEN8_MASTER_IRQ`, `GEN11_GU_MISC_ISR/IMR/IIR/IER`, `GEN11_GFX_MSTR_IRQ`, `SCPD0`, `VLV_IIR_RW`, `VLV_IER/IIR/IMR/ISR`, and `VLV_PCBR`.

Control flow: interrupt setup code programs masks/enables, reads ISR/IIR, routes master bits to display/GT/PCU/GU handlers, and acknowledges sources. Macros such as `GEN8_DE_PIPE_IRQ(pipe)` generate per-pipe bits.

State and persistence: hardware interrupt enable/mask/status registers are mutable device state. This header defines addresses and bits but no software state.

Dependencies and integration: expects `_MMIO`, `I915_IRQ_REGS`, and platform display base macros from Intel register infrastructure. Integrated by i915/xe interrupt code.

Risks and test signals: overlapping bit aliases across generations must be applied only to correct hardware. Tests should cover interrupt storms, vblank delivery per pipe, hotplug/port IRQs, GU miscellaneous IRQs, suspend/resume register restore, and platform-specific mask programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/intel_gmd_interrupt_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/intel_gmd_misc_regs.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/intel_gmd_misc_regs.h

Purpose: defines miscellaneous Intel graphics/display MMIO registers used for display arbitration, FBC behavior, tiling swizzle, and instruction/power-management control.

Important APIs/types/functions: `DISP_ARB_CTL` carries `DISP_FBC_MEMORY_WAKE`, `DISP_TILE_SURFACE_SWIZZLING`, and `DISP_FBC_WM_DIS`. `INSTPM` carries legacy self-enable, AGPBUSY interrupt enable, force ordering, TLB invalidate, and sync flush bits.

Control flow: display and GT init paths read/modify/write these registers to configure memory arbitration, FBC behavior, tiling surface interpretation, ordering, and flush/invalidate operations.

State and persistence: the state is hardware register state that may be reprogrammed at init and resume. No software state is declared.

Dependencies and integration: expects `_MMIO`, `REG_BIT`, and Intel register access helpers. Integrated by display watermark/FBC and GT flush paths.

Risks and test signals: wrong bit use can break framebuffer compression, tiling, interrupt delivery from low power states, or TLB coherency. Test FBC enable/disable, tiled framebuffer scanout, suspend/resume, and forced flush/invalidate paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/intel_gmd_misc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/intel_lb_mei_interface.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/intel_lb_mei_interface.h

Purpose: defines the Intel late-binding MEI component interface for authenticated firmware/configuration payload delivery.

Important APIs/types/functions: `INTEL_LB_FLAG_IS_PERSISTENT` requests flash persistence across warm resets. `enum intel_lb_type` identifies fan-control and Ocode payloads. `enum intel_lb_status` maps firmware response statuses including 4ID mismatch, arbitration failure, invalid signature/payload/FPT/manifest/hash, SVN failure, destination mailbox failure, invalid command/header, timeout, and internal IP errors. `struct intel_lb_component_ops` exposes `push_payload()`.

Control flow: a consumer calls `push_payload(dev, type, flags, payload, payload_size)` on the MEI device. The provider returns 0 on success, negative errno for transport failures, or positive firmware status.

State and persistence: payload persistence is firmware-controlled via the persistent flag. The header itself stores no state.

Dependencies and integration: depends on Linux bit and type helpers plus `struct device`. Integrated by Intel graphics/platform code and MEI late-binding service providers.

Risks and test signals: risks include confusing positive firmware status with errno, mishandling persistent payloads, and accepting wrong payload type/signature. Test all status translations, persistent/nonpersistent payloads, payload-size validation, and MEI disconnect/retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/intel_lb_mei_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/intel_lpe_audio.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/intel_lpe_audio.h

Purpose: describes platform data exchanged with the Intel HDMI LPE audio platform device used on some low-power Intel SoCs.

Important APIs/types/functions: `HDMI_MAX_ELD_BYTES` is 128. `struct intel_hdmi_lpe_audio_port_pdata` carries ELD bytes, port, pipe, link-symbol clock, and DisplayPort/HDMI output flag. `struct intel_hdmi_lpe_audio_pdata` contains three port records for ports B/C/D, number of ports, number of pipes, a `notify_audio_lpe()` callback, and `lpe_audio_slock`.

Control flow: display code fills/updates ELD and port/pipe metadata, notifies the LPE audio platform device on relevant port changes, and protects shared audio state with the spinlock.

State and persistence: runtime ELD and routing state lives in platform data. It changes on hotplug/modeset and is not persistent across driver lifecycle.

Dependencies and integration: depends on Linux types, spinlock types, and `struct platform_device`. Integrated by Intel display/audio glue and the HDMI LPE audio driver.

Risks and test signals: stale ELD, wrong port indexing, and missing locking can break audio routing. Test hotplug, DP vs HDMI output flagging, all three ports, concurrent notification, and sample-rate/ELD propagation to userspace audio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/intel_lpe_audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/intel_pcode_regs.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/intel_pcode_regs.h

Purpose: defines Intel PCODE mailbox MMIO register, command fields, status codes, and mailbox command payload helpers used for power, display frequency, memory latency, SAGV, CDCLK, TCCOLD, HDCP key load, and frequency configuration.

Important APIs/types/functions: `GEN6_PCODE_MAILBOX` and fields such as ready bit, param masks, command mask, and error values are central. Command constants include RC6 voltage read/write, display frequency change request, memory latency reads, HDCP keys, CDCLK control, min frequency table, OC params, memory subsystem info, SAGV configuration, TCCOLD, IPS, dynamic duty cycle, DG1 status, power setup, SAGV block time, and XeHP frequency config. Helpers encode/decode RC6 VID and prepare CDCLK/pipe-count/voltage fields.

Control flow: pcode interface code writes mailbox command/params, waits for ready/status, decodes replies and errors, and retries or fails based on platform-specific status values.

State and persistence: PCODE firmware holds persistent platform power/frequency state; mailbox requests transiently update or query it.

Dependencies and integration: expects `_MMIO`, `REG_GENMASK`, `REG_BIT`, and `REG_FIELD_PREP`. Integrated by Intel display power management, CDCLK, SAGV, IPS, and GT frequency code.

Risks and test signals: command/status values vary by generation. Wrong masks or status interpretation can hang display power changes or memory frequency transitions. Test pcode timeout/error paths, CDCLK transitions, SAGV enable/disable, TCCOLD entry/exit, and platform-specific mailbox command coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/intel_pcode_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/pciids.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/pciids.h

Purpose: provides Intel graphics PCI ID macro lists used by i915/xe and helper modules to build device ID tables without duplicating large ID arrays.

Important APIs/types/functions: `INTEL_PCI_DEVICE`, `INTEL_VGA_DEVICE`, and `INTEL_QUANTA_VGA_DEVICE` expand IDs into PCI table initializers. Generation/family macros group IDs from i810/i815/i830/i845/i85x/i865/i915/i945/i965/G33/GM45/G45 through Pineview, Ironlake, Sandy/Ivy Bridge, Haswell, Valleyview, Broadwell, Cherryview, Skylake, Broxton, Gemini Lake, Kaby/Coffee/Comet/Whiskey/Cannon/Ice/Tiger/Rocket/Jasper/Elkhart, DG1/DG2/ATS, Alder/Raptor/Arrow/Meteor/Ponte Vecchio/Lunar/Battlemage/Panther/Wildcat/Nova/CRI and related product families.

Control flow: no runtime code. Driver PCI tables invoke family macros with an initializer macro and per-device info pointer or flags, producing compile-time arrays for device matching and module autoloading.

State and persistence: PCI IDs are stable hardware identification data. The header does not store runtime state but defines long-lived driver matching ABI within the kernel source.

Dependencies and integration: expects Linux PCI table structures and vendor constants. Integrated by i915, xe, backlight/display helpers, and any Intel graphics module needing matched device lists.

Risks and test signals: duplicate IDs, missing IDs, wrong family grouping, or wrong info pointer can bind the wrong driver path. Test via `modinfo` aliases, PCI table build coverage, probe on representative SKUs, and automated duplicate-ID scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/pciids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/pick.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/pick.h

Purpose: supplies compact compile-time macros for selecting indexed MMIO offsets or constants from evenly spaced ranges or explicit value lists.

Important APIs/types/functions: `_PICK_EVEN(index, a, b)` computes an arithmetic progression. `_PICK_EVEN_2RANGES(index, c_index, a, b, c, d)` selects from one even range before `c_index` and a second after it, requiring `c_index` to be constant. `_PICK(index, ...)` indexes an anonymous constant `u32` array for irregular values.

Control flow: macro expansion performs constant or runtime arithmetic/indexing inside register definitions. There are no functions or side effects except build-time validation in the two-range form.

State and persistence: none.

Dependencies and integration: uses `BUILD_BUG_ON_ZERO` and `__is_constexpr`; integrated by Intel register headers for pipe/port/transcoder indexed MMIO address generation.

Risks and test signals: risks include nonconstant cutoff in two-range use, out-of-range array indexing in `_PICK`, and unintended multiple evaluation of index expressions. Test by compiling register headers for all platforms and checking generated MMIO addresses against hardware specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/pick.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/reg_bits.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/reg_bits.h

Purpose: wraps generic kernel bitfield helpers in Intel register-oriented macros with explicit width casts and integer-constant-expression validation.

Important APIs/types/functions: width-specific masks and bits include `REG_GENMASK*` and `REG_BIT*`. Field helpers include `REG_FIELD_PREP8`, `REG_FIELD_PREP16`, `REG_FIELD_PREP`, `REG_FIELD_GET8`, `REG_FIELD_GET`, `REG_FIELD_GET64`, and `REG_FIELD_MAX`. Masked write helpers include `REG_MASKED_FIELD`, `REG_MASKED_FIELD_ENABLE`, and `REG_MASKED_FIELD_DISABLE`.

Control flow: these macros are expanded inside register definitions and register-write values. Prep macros validate mask constness, width, power-of-two field shape, and constant value range with build bugs; runtime values are shifted and masked.

State and persistence: none. They affect how register values are encoded before hardware writes.

Dependencies and integration: depends on `linux/bitfield.h` and `linux/bits.h`. Used throughout Intel DRM MMIO register definitions.

Risks and test signals: incorrect masks should fail compilation when constant. Remaining risks are side effects in macro arguments and misuse of 16-bit masked-field protocol. Test with build coverage, sparse/compile warnings, unit-style constant expression checks, and hardware register write traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/reg_bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/step.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/step.h

Purpose: defines a common symbolic Intel stepping enumeration for display and GT code.

Important APIs/types/functions: `STEP_NAME_LIST(func)` enumerates A0 through J3 by applying a callback macro. `STEP_ENUM_VAL(name)` maps names to `STEP_name`. `enum intel_step` includes `STEP_NONE`, all generated step names, `STEP_FUTURE`, and `STEP_FOREVER`.

Control flow: no runtime logic. Other code can reuse `STEP_NAME_LIST` to generate string tables, comparisons, or switch cases consistently.

State and persistence: none. The enum values are symbolic software compatibility markers and may not map directly to hardware encodings.

Dependencies and integration: standalone macro/enum header. Integrated by Intel platform stepping tables, workarounds, and display/GT feature gating.

Risks and test signals: ordering is part of comparison semantics; inserting values in the wrong place can change workaround ranges. Test platform stepping decode, workaround table boundaries, and compile-time generation of any parallel name arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/step.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/xe_sriov_vfio.h -->
# sources/distributed-fs/ceph-client/include/drm/intel/xe_sriov_vfio.h

Purpose: declares the interface used by VFIO migration code to coordinate Intel Xe SR-IOV virtual function control through the physical function driver.

Important APIs/types/functions: functions obtain a PF `xe_device` from a VF `pci_dev`, check migration support, prepare/wait for FLR, suspend/resume a VF, enter/exit stop-copy save, enter/exit resume-data restore, move a VF to error state, read/write migration data to userspace buffers, and estimate stop-copy data size.

Control flow: VFIO asks for the PF object, validates migration support, coordinates FLR, then drives migration state transitions. Stop-copy and resume-data phases bracket streaming reads/writes of migration payloads; failures can move the VF into an error state requiring reset.

State and persistence: migration, suspend, FLR pending/done, and error states are maintained in PF/VF driver and firmware state outside this header. Userspace buffers carry transient migration data.

Dependencies and integration: depends on PCI, Xe device, Linux types, and `char __user` user-memory pointers. Integrated by Xe SR-IOV PF code and VFIO PCI migration support.

Risks and test signals: VF ID 0 is invalid, user-copy paths must handle partial read/write and errno, and state-transition ordering matters. Test VF migration happy path, FLR timeout, suspend/resume across all tiles, partial data streaming, unsupported migration, and error-state recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/intel/xe_sriov_vfio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/spsc_queue.h -->
# sources/distributed-fs/ceph-client/include/drm/spsc_queue.h

Purpose: implements a small lockless single-producer/single-consumer queue used by DRM scheduler-style code.

Important APIs/types/functions: `struct spsc_node` is the embedded link. `struct spsc_queue` stores consumer `head`, atomic `tail` pointer-to-next, and atomic `job_count`. Inline operations are `spsc_queue_init()`, `spsc_queue_peek()`, `spsc_queue_count()`, `spsc_queue_push()`, and `spsc_queue_pop()`.

Control flow: initialization points `tail` at `head`. Producer disables preemption, increments count, atomically swaps `tail` to the new node's `next`, links the previous tail pointer to the node, uses a write barrier, and returns whether the queue was empty. Consumer reads `head`, advances to `next`, and on last-element slow path CASes `tail` back to `head` or waits until a concurrent producer publishes `next`.

State and persistence: queue state is in `head`, `tail`, and `job_count`. It is runtime-only and assumes exactly one producer and one consumer.

Dependencies and integration: depends on atomics, preemption control, and memory barriers. Integrated by DRM scheduler/job queues where SPSC assumptions hold.

Risks and test signals: using multiple producers or consumers breaks correctness. Barriers, last-element slow path, and job count accuracy are critical. Test empty-to-nonempty wake decisions, concurrent push/pop stress, preemption-sensitive producer paths, and count underflow/overflow assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/spsc_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/task_barrier.h -->
# sources/distributed-fs/ceph-client/include/drm/task_barrier.h

Purpose: provides an inline reusable two-phase task barrier for a fixed number of cooperating kernel tasks.

Important APIs/types/functions: `struct task_barrier` stores participant count `n`, atomic `count`, and enter/exit semaphores. Helpers initialize, add/remove tasks, signal a turnstile `n` times, enter, exit, and run a full barrier.

Control flow: in `task_barrier_enter()`, each task increments `count`; the last entrant opens the enter turnstile for all participants, then every task waits on it. In `task_barrier_exit()`, each task decrements `count`; the last exiting task opens the exit turnstile, preventing any task from running ahead when the barrier is reused.

State and persistence: state is runtime semaphore/count state. The participant count must be stable during an active barrier cycle.

Dependencies and integration: depends on Linux semaphores and atomics. Used by DRM/driver code needing repeated rendezvous among kernel tasks.

Risks and test signals: changing `n` while tasks are blocked, missing participants, or failing tasks cause deadlock. Comments contain minor spelling issues but no behavior. Test repeated cycles, add/remove before use, signal interruption behavior of `down()`, and timeout wrappers in callers if deadlock risk exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/task_barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_allocation.h -->
# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_allocation.h

Purpose: defines allocation policy flags shared by TTM page pools and devices.

Important APIs/types/functions: `TTM_ALLOCATION_POOL_BENEFICIAL_ORDER(n)` stores the maximum high-order allocation useful to the caller in low 8 bits. `TTM_ALLOCATION_POOL_USE_DMA_ALLOC` requests coherent DMA allocations. `TTM_ALLOCATION_POOL_USE_DMA32` requests DMA32-capable pages. `TTM_ALLOCATION_PROPAGATE_ENOSPC` preserves resource-manager `-ENOSPC` instead of converting it to `-ENOMEM`.

Control flow: no functions. TTM pool/device initialization and allocation paths consume these bits to select allocation backend, DMA zone, and error propagation.

State and persistence: flags become persistent policy in `ttm_device` or `ttm_pool` instances for their lifetime.

Dependencies and integration: relies on `BIT()` being available from includers. Used by `ttm_device.h`, `ttm_pool.h`, and BO allocation paths.

Risks and test signals: overlapping low-order values with policy bits or losing `ENOSPC` semantics can change eviction behavior. Test DMA32 allocations, coherent DMA pool use, high-order fallback, and expected errno from exhausted resource managers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_allocation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_backup.h -->
# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_backup.h

Purpose: declares TTM backup storage helpers for temporarily replacing pages with opaque handles backed by shmem during shrink/backup operations.

Important APIs/types/functions: inline helpers encode a backup handle as an invalid `struct page *` with the low bit set, detect such handles, and decode them back. External APIs drop a backup handle, copy a backed-up page into a destination page, back up a page, finalize backup storage, query available backup bytes, and create a shmem backup file.

Control flow: backup code creates shmem storage, backs pages up by handle, stores encoded handles in page arrays, later copies or drops them, and finalizes the storage file.

State and persistence: backup state is in the shmem `struct file` and encoded page-array handles. It is runtime swap/backup state, not durable persistence.

Dependencies and integration: depends on memory management and shmem headers. Integrated by TTM TT backup, pool backup/restore, and BO shrinking.

Risks and test signals: low-bit pointer tagging assumes real page pointers are aligned. Mishandling handles as real pages can crash. Test mixed page/handle arrays, backup/drop/copy ordering, low-memory behavior, writeback modes, and cleanup of shmem files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_backup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_bo.h -->
# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_bo.h

Purpose: defines the core TTM buffer object API for GEM-backed graphics memory objects, placement validation, reservation, eviction/shrinking, CPU mappings, VM faults, moves, pinning, and LRU walks.

Important APIs/types/functions: `enum ttm_bo_type`, `struct ttm_buffer_object`, `ttm_bo_kmap_obj`, `ttm_operation_ctx`, LRU walk structures, shrink flags, reserve/unreserve helpers, validation/init/fini, kmap/vmap/mmap/fault/access APIs, memory-space allocation, move helpers, populate/setup export, pin/unpin, eviction/swapout, and guarded LRU cursor iteration.

Control flow: callers initialize a BO with placement and optional SG/reservation, reserve it via dma-resv/ww mutexes, validate or move it to a compatible `ttm_resource`, attach fences on submission, unreserve to return it to LRU, and later fault/map/access/pin/evict/shrink/swap as needed. Inline reserve paths convert interrupted waits to `-ERESTARTSYS` and no-wait reservation to `-EBUSY`.

State and persistence: BO state includes GEM base, bdev, type, resource, TT backing, deletion flag, bulk move, priority, pin count, delayed delete work, and external SG table. Most mutable members require reservation lock; LRU operations require device LRU lock.

Dependencies and integration: depends on DRM GEM, dma-resv/fence, VM, TTM device/resource/placement/TT, kmap iterators, workqueues, and scatter-gather. It is central to TTM-using DRM drivers.

Risks and test signals: locking order, deadlock handling, delayed deletion, fence synchronization, resource transitions, CPU mapping cache policy, and VM fault behavior are high risk. Test multi-BO reservation with deadlock backoff, eviction under pressure, pin/unpin, mmap faults, panic kmap, shrink/backup, SG BOs, and suspend/hibernation swapout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_bo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_caching.h -->
# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_caching.h

Purpose: defines TTM CPU caching policy names and the conversion entry point to page protections.

Important APIs/types/functions: `TTM_NUM_CACHING_TYPES` is 3. `enum ttm_caching` covers `ttm_uncached`, `ttm_write_combined`, and `ttm_cached`. `ttm_prot_from_caching()` converts a caching enum and base `pgprot_t` into the mapping protection to use.

Control flow: allocation, mapping, and fault paths choose an enum based on placement/device requirements and ask `ttm_prot_from_caching()` for CPU PTE attributes.

State and persistence: caching policy is stored in TTM TT/resources and affects mappings while present.

Dependencies and integration: depends on Linux page-table types. Integrated by TTM TT, pool, BO mapping, and resource mapping code.

Risks and test signals: wrong cache policy can cause incoherent GPU/CPU access or slow mappings. Test cached/write-combined/uncached mmap and kmap paths, device snooping assumptions, and architecture-specific pgprot output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_caching.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_device.h -->
# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_device.h

Purpose: declares the TTM per-device object, global state, driver callback table, initialization/finalization, manager access, hibernation, swapout, and DMA mapping cleanup.

Important APIs/types/functions: `ttm_glob` contains dummy read page, device list, and global BO count. `struct ttm_device_funcs` lets drivers create/populate/unpopulate/destroy TT, judge eviction value, choose evict placement, move BOs, receive delete/swap/release notifications, reserve/free IO memory, compute IO PFNs, and perform ptrace-style memory access. `struct ttm_device` stores device list, allocation flags, funcs, system manager, per-memory-type managers, VMA manager, page pool, LRU lock, unevictable list, dev mapping, and delayed-delete workqueue.

Control flow: a driver initializes `ttm_device`, installs memory managers, creates BOs, and TTM calls driver callbacks during validation, eviction, swapout, mapping, and release. `ttm_manager_type()` and `ttm_set_driver_manager()` access manager slots with constant-bound checks.

State and persistence: per-device managers, pool, LRU lists, unevictable BOs, and workqueue are persistent for the DRM device lifetime. Global state tracks all TTM devices and BO count.

Dependencies and integration: depends on TTM allocation/resource/pool headers, DRM VMA offset management, workqueues, address_space, and driver memory callbacks.

Risks and test signals: callback misimplementation, manager slot misuse, pool cleanup, LRU locking, and hibernation/swapout are critical. Test device init/fini leaks, manager registration bounds, BO create/destroy counts, global/device swapout, hibernation preparation, and DMA mapping cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_execbuf_util.h -->
# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_execbuf_util.h

Purpose: provides helper contracts for reserving and fencing multiple TTM buffer objects during command submission.

Important APIs/types/functions: `struct ttm_validate_buffer` links a BO and requested shared fence count into a private validation list. APIs are `ttm_eu_reserve_buffers()`, `ttm_eu_backoff_reservation()`, and `ttm_eu_fence_buffer_objects()`.

Control flow: command submission builds a validation list, calls reserve with a `ww_acquire_ctx`, handles deadlock retries/duplicates/signal interruption, validates or emits commands, then either backs off reservations on failure or attaches a fence to all BOs and unreserves on success.

State and persistence: list entries hold temporary references and reservation state. Fences added on success persist in BO reservation objects until signaled/retired.

Dependencies and integration: depends on lists, ww mutex contexts, dma_fence, and TTM BOs. Used by TTM-based DRM drivers' execbuffer paths.

Risks and test signals: deadlock handling and duplicate BO behavior are the main risk. Test reversed-order reservations from competing threads, duplicate list entries with and without `dups`, interruptible waits, no leaked reservations on errors, and fence propagation to all BOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_execbuf_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_kmap_iter.h -->
# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_kmap_iter.h

Purpose: defines a generic iterator interface for page-sized local kernel mappings of TTM resources.

Important APIs/types/functions: `struct ttm_kmap_iter_ops` provides `map_local()`, `unmap_local()`, and `maps_tt`. `struct ttm_kmap_iter` holds the ops pointer and is embedded by TT/resource-specific iterators.

Control flow: copy/move code initializes a specialized iterator, maps a page index into an `iosys_map`, copies or clears data, and unmaps it before moving to the next page. `maps_tt` distinguishes direct TT pages from aperture-backed TT resources.

State and persistence: iterator state is transient and specialization-specific. No backing memory is owned by this base header.

Dependencies and integration: depends on Linux types and `iosys_map`. Implemented by TT and resource IO mapping helpers, consumed by TTM memcpy move and CPU copy paths.

Risks and test signals: local mapping lifetime must be short and paired. Test page-by-page moves across TT, IO memory, and linear resources, highmem/local mapping correctness, and cleanup on copy errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_kmap_iter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_placement.h -->
# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_placement.h

Purpose: defines TTM placement domains, placement flags, and the structures drivers pass to choose valid memory locations for BOs.

Important APIs/types/functions: memory domains include `TTM_PL_SYSTEM`, `TTM_PL_TT`, `TTM_PL_VRAM`, and driver-private start `TTM_PL_PRIV`. Flags request contiguous allocation, top-down search, temporary placement during eviction, desired placement, and fallback placement. `struct ttm_place` stores PFN range, memory type, and flags. `struct ttm_placement` stores an array of preferred places.

Control flow: BO validation and eviction walk candidate placements, allocate a compatible resource in the requested manager, and may fall back or use temporary placements based on flags.

State and persistence: placement structures are caller-provided policy; selected placement becomes BO `ttm_resource` state.

Dependencies and integration: depends on fixed-width Linux types. Used by TTM BO validation, resource allocation, eviction, and driver placement tables.

Risks and test signals: wrong PFN limits or fallback ordering can evict excessively or allocate inaccessible memory. Test VRAM/system/TT placement, top-down and contiguous constraints, eviction fallback, and driver private memory types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_placement.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_pool.h -->
# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_pool.h

Purpose: declares the TTM page pool that caches pages by caching mode and allocation order, with backup/restore and debug support.

Important APIs/types/functions: `struct ttm_pool_type` describes one order/caching pool with shrinker list and `list_lru`. `struct ttm_pool` stores device, NUMA node, allocation flags, and per-caching arrays of pool types. APIs allocate/free TT pages, initialize/finalize pools, print debugfs state, drop backed-up pages, back up and restore TT memory, and initialize/finalize the global pool manager.

Control flow: TT population requests pages from the pool according to caching and allocation flags; unpopulation returns pages. Shrink/backup paths can move pages to backup storage and restore them on demand.

State and persistence: pools persist for device or global manager lifetime and own cached pages in LRU lists. Backup state is linked to TT structures.

Dependencies and integration: depends on page orders, lockless lists, spinlocks, list_lru, caching, backup flags, operation contexts, and TT. Integrated by TTM device and TT population.

Risks and test signals: page accounting, caching mismatch, DMA32/coherent allocation policy, and backup restore are key risks. Test pool alloc/free under pressure, shrinker behavior, debugfs output, backed-up TT restore, NUMA/device constraints, and manager init/fini leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_range_manager.h -->
# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_range_manager.h

Purpose: declares a DRM-MM-backed TTM resource manager for range-based address spaces such as VRAM apertures.

Important APIs/types/functions: `struct ttm_range_mgr_node` extends `ttm_resource` with a flexible array of `drm_mm_node`s. `to_ttm_range_mgr_node()` downcasts from base resource. `ttm_range_man_init_nocheck()` and `ttm_range_man_fini_nocheck()` install/remove the manager; inline checked wrappers validate constant memory type bounds.

Control flow: driver init registers a range manager for a memory type and size. Resource allocation uses DRM MM nodes behind the manager; fini removes it when empty.

State and persistence: range manager state lives in the TTM device manager slot and DRM MM nodes embedded in resources.

Dependencies and integration: depends on TTM resource/device and DRM MM. Used by TTM drivers for VRAM or other linear address spaces.

Risks and test signals: finishing with live allocations, wrong memory type index, and multi-node resource handling are risks. Test manager init/fini, allocation/free fragmentation, bound checks, and eviction of all resources before fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_range_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_resource.h -->
# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_resource.h

Purpose: defines TTM resource managers, resource objects, LRU infrastructure, bulk moves, cursors, bus placements, IO/kmap iterators, allocation/free APIs, eviction, debug, and manager iteration.

Important APIs/types/functions: constants define memory-type and priority limits. Types include `ttm_lru_item`, `ttm_resource_manager_func`, `ttm_resource_manager`, `ttm_bus_placement`, `ttm_resource`, `ttm_lru_bulk_move`, `ttm_resource_cursor`, `ttm_kmap_iter_iomap`, and `ttm_kmap_iter_linear_io`. APIs initialize/finalize managers/resources, allocate/free resources, test intersections/compatibility, set BO back-pointers, bulk-move LRU ranges, evict all resources, report usage/debug, iterate LRUs, initialize IO mapping iterators, and create debugfs entries.

Control flow: BO validation asks the appropriate manager to allocate a resource for a `ttm_place`. Resources are attached to BOs, placed on priority LRUs, moved in bulk for command submission locality, evicted by resource-manager walks, and freed through the manager callback.

State and persistence: managers track usage, size, enablement, eviction fences, LRU lists, optional cgroup region, and driver funcs. Resources store placement, bus mapping, weak BO reference, cgroup charge, and LRU node.

Dependencies and integration: depends on Linux lists, mutex/spinlock/fence, iosys-map, TTM caching/kmap, DRM printer/debugfs, io_mapping, SG, and memory cgroups. It is the lower layer used by TTM BO/device/range-manager code.

Risks and test signals: LRU locking, weak BO references, eviction fence cleanup, manager usage accounting, cgroup charging, and iterator hitch correctness are high risk. Test resource allocation/free, LRU iteration during mutation, bulk moves, evict-all, debug output, IO map iterators, and manager disable with nonempty LRUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_tt.h -->
# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_tt.h

Purpose: declares Translation Table backing storage for BOs not directly backed by fixed VRAM/AGP memory, including page arrays, DMA addresses, swap/backup storage, caching, population, swap, backup/restore, kmap iterator support, and optional AGP backend.

Important APIs/types/functions: `struct ttm_tt` stores pages, flags, page count, SG table, DMA addresses, swap and backup files, caching, and restore state. Flags describe swapped, zero-alloc, external, external-mappable, decrypted, backed-up, and private-populated states. `struct ttm_kmap_iter_tt` adapts TT pages to kmap iteration. APIs create/init/fini/destroy TT, populate/unpopulate, swap in/out, mark for clear, initialize global TT manager, initialize TT kmap iterator, query page limit, configure backup, backup/restore TT, and optional AGP create/bind/unbind/destroy/is_bound.

Control flow: BO creation creates a TT without pages, validation/population allocates or restores pages, moves bind them into aperture resources, shrink/swap backs or swaps them out, and destroy unbinds/unpopulates/frees backend state.

State and persistence: TT state is the page vector plus flags and backup/swap handles. External flags prevent TTM from swapping or mapping externally owned pages directly.

Dependencies and integration: depends on pagemap, caching, kmap iterator, TTM device/resource/BO, pool backup, shmem, DMA, SG, and optional AGP.

Risks and test signals: external page handling, backup flag clearing, decrypted pgprot assumptions, population flag correctness, and AGP binding are key risks. Test populate/unpopulate, swapout/swapin, backup/restore, external SG/userptr pages, zero allocation, decrypted mappings, and AGP builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/ttm/ttm_tt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/arm/coresight-cti-dt.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/arm/coresight-cti-dt.h

Purpose: defines numeric device-tree constants for ARM CoreSight CTI trigger signal types.

Important APIs/types/functions: constants enumerate generic IO/interrupt/halt/restart triggers, PE debug and PMU triggers, ETM external in/out, sink full/acquire/flush signals, STM timeout/event signals, ELA trace start/stop/debug request, and `CTI_TRIG_MAX`.

Control flow: DTS files reference these IDs in CTI trigger descriptions; CoreSight CTI drivers parse the numeric cells and configure trigger routing.

State and persistence: IDs are device-tree ABI and must remain stable. No runtime state is held in the header.

Dependencies and integration: standalone DT binding header integrated by ARM CoreSight device trees and CTI driver bindings.

Risks and test signals: renumbering breaks existing DTBs. Test schema validation, CTI trigger routing on supported SoCs, and bounds checking against `CTI_TRIG_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/arm/coresight-cti-dt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/arm/mhuv3-dt.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/arm/mhuv3-dt.h

Purpose: defines device-tree constants for ARM MHUv3 extension channel types.

Important APIs/types/functions: `DBE_EXT`, `FCE_EXT`, and `FE_EXT` assign numeric IDs for the defined MHUv3 extension classes.

Control flow: DTS bindings use these constants in MHUv3 channel/type cells; the driver interprets them when instantiating mailbox resources.

State and persistence: constants are stable DT ABI values.

Dependencies and integration: standalone DT binding used by ARM mailbox/MHUv3 device trees and drivers.

Risks and test signals: incorrect IDs break mailbox channel discovery. Test dt-schema examples and MHUv3 probe using each extension type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/arm/mhuv3-dt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/arm/qcom,ids.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/arm/qcom,ids.h

Purpose: defines Qualcomm SoC and board identifiers used by bootloaders, older `qcom,msm-id`/`qcom,board-id` device-tree properties, and the socinfo driver.

Important APIs/types/functions: `QCOM_ID_*` constants map many MSM/APQ/MDM/IPQ/SDM/SM/SC/SA/QCM/QCS/X1/QDU/QRU/QCF/CQ product names to numeric chipset IDs. `QCOM_BOARD_ID(a, major, minor)` encodes board type plus major/minor revision. Board type constants include MTP, DragonBoard, QRD, and SBC.

Control flow: firmware or DT provides numeric IDs; platform code and socinfo match them to SoC/board revisions for compatibility handling.

State and persistence: IDs are ABI with boot firmware and DTBs. They must not be renumbered once published.

Dependencies and integration: standalone DT binding included by Qualcomm DTS files and referenced by socinfo/platform code.

Risks and test signals: duplicate or wrong numeric values can select wrong compatibility data. Test duplicate-ID scans, dt-schema validation for legacy properties, socinfo output, and boot on representative old/new Qualcomm boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/arm/qcom,ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/arm/ux500_pm_domains.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/arm/ux500_pm_domains.h

Purpose: defines Ux500 power-domain IDs for device-tree consumers.

Important APIs/types/functions: `DOMAIN_VAPE` is domain 0 and `NR_DOMAINS` derives the domain count.

Control flow: DTS power-domain references use the ID; PM domain provider code indexes the corresponding domain.

State and persistence: the numeric ID is DT ABI. No runtime state is stored.

Dependencies and integration: standalone binding used by Ux500 DTS and generic PM domain provider/consumers.

Risks and test signals: adding domains requires preserving existing IDs and updating `NR_DOMAINS`. Test DT references and genpd provider registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/arm/ux500_pm_domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/ata/ahci.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/ata/ahci.h

Purpose: exposes AHCI device-tree capability bit constants for generic HBA and port properties.

Important APIs/types/functions: HBA capability bits include `HBA_SSS` and `HBA_SMPS`. Port capability bits include hot-plug capable, mechanical presence switch, cold presence detect, external SATA port, and FIS-based switching capable.

Control flow: DTS properties use these bit values; AHCI platform drivers read the properties and set or override hardware capability fields.

State and persistence: constants are DT ABI; runtime state is in driver capability masks.

Dependencies and integration: standalone binding for AHCI platform DT nodes and libahci/platform drivers.

Risks and test signals: wrong bit positions enable or disable SATA features incorrectly. Test DT schema, platform probe capability masks, hotplug, staggered spin-up, and external/FBS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/ata/ahci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/bus/moxtet.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/bus/moxtet.h

Purpose: defines interrupt indexes for the Turris Mox Moxtet module configuration bus.

Important APIs/types/functions: constants assign PCI IRQ 0, USB3 IRQ 4, Peridot IRQs as `8 + n`, and Topaz IRQ 12.

Control flow: DTS interrupt specifiers use these indexes; the Moxtet bus/IRQ code maps them to module events.

State and persistence: IDs are stable DT ABI for Turris Mox modules.

Dependencies and integration: standalone DT binding used by Moxtet device trees and bus driver IRQ mapping.

Risks and test signals: wrong indexes misroute module interrupts. Test DTS validation and IRQ delivery for PCI, USB3, Peridot, and Topaz modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/bus/moxtet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/bus/ti-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/bus/ti-sysc.h

Purpose: defines TI sysc interconnect target-module bit constants and idle-mode values for OMAP/AM/DRA device trees.

Important APIs/types/functions: constants cover OMAP2 clockactivity/emufree/wakeup/softreset/autoidle, OMAP4 DMA disable/freeemu/softreset, SmartReflex wakeup, DRA7 MCAN wakeup, PRUSS standby/submodule wait bits, and `SYSC_IDLE_FORCE`, `SYSC_IDLE_NO`, `SYSC_IDLE_SMART`, `SYSC_IDLE_SMART_WKUP`.

Control flow: DTS sysc nodes encode supported bits and idle modes; the sysc driver writes module SYSCONFIG registers and manages reset/idle transitions.

State and persistence: constants are DT ABI. Runtime state is target-module register configuration.

Dependencies and integration: standalone binding used by TI OMAP/AM/DRA DTS files and sysc interconnect driver.

Risks and test signals: wrong bit values can break reset, wakeup, or idle behavior. Test suspend/resume, module idle transitions, PRUSS and MCAN wakeup, and dt-schema coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/bus/ti-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/actions,s500-cmu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/actions,s500-cmu.h

Purpose: defines Actions Semi S500 CMU clock IDs for device-tree clock consumers.

Important APIs/types/functions: IDs cover fixed LOSC/HOSC, core/device/DDR/NAND/display/ethernet/audio PLLs, system clocks, display/video engines, timers, I2C, PWM, SD, sensors, SPI, UART, HDMI, SPDIF, NAND/ECC, RMII, GPIO, APB, DMAC, NIC, Ethernet, and `CLK_NR_CLKS`.

Control flow: DTS `clocks` cells use IDs; the S500 clock driver registers matching providers and resolves consumer requests.

State and persistence: numeric IDs are DT ABI and stable once published.

Dependencies and integration: standalone clock binding included by S500 DTS and CMU driver.

Risks and test signals: ID renumbering or count mismatch breaks consumers. Test `CLK_NR_CLKS`, clock lookup for every referenced DTS ID, and enable/rate operations for core peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/actions,s500-cmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/actions,s700-cmu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/actions,s700-cmu.h

Purpose: defines Actions Semi S700 CMU clock IDs for DT consumers and the S700 clock provider.

Important APIs/types/functions: IDs include PLLs, CPU/device/AHB/APB/DMAC/NOC/high-performance clock muxes/dividers, sensor source, GPIO, DSI/CSI/display/video engines, NAND/SD, UART, PWM, GPU3D, I2C, SPI, USB2/USB3 PHY/MAC/CCE clocks, LCD/HDMI/I2S, sensors, Ethernet/RMII, TVOUT, thermal sensor, IRC switch, PCM1, and `CLK_NR_CLKS`.

Control flow: clock specifiers in DTS map to provider registrations in the S700 CMU driver.

State and persistence: constants are stable DT ABI.

Dependencies and integration: standalone clock binding for S700 platform DTS and drivers.

Risks and test signals: consumer/provider table mismatch, especially with USB and display clocks. Test clock tree registration count, DTS references, rate parent selection, and peripheral probe for USB, display, audio, and Ethernet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/actions,s700-cmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/actions,s900-cmu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/actions,s900-cmu.h

Purpose: defines Actions Semi S900 CMU clock IDs for fixed clocks, PLLs, system clocks, display/video, GPU, I/O, USB, DDR, and Ethernet.

Important APIs/types/functions: constants cover LOSC/HOSC, core/device/DDR/NAND/display/DSI/assist/audio PLLs, CPU/device/NOC/AHB/APB/DMAC, GPIO, BISP/CSI/display engines, DSI, GPU core/memory/sys, I2C, I2S, IMX, LCD, NAND, PWM, SD, sensors, SPI, thermal, UART, VCE/VDE, USB2/USB3, timer, HDMI audio, 24M/eDP clocks, DDR/DMM, Ethernet MAC/RMII, and `CLK_NR_CLKS`.

Control flow: S900 DTS clock specifiers select IDs consumed by the clock controller driver.

State and persistence: IDs are stable DT ABI.

Dependencies and integration: standalone Actions S900 clock binding.

Risks and test signals: gaps in numeric space must match provider arrays. Test clock provider registration, display/eDP/USB/DDR clock lookup, and DTS schema references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/actions,s900-cmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/agilex-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/agilex-clock.h

Purpose: defines Intel/Altera Agilex SoC clock IDs for DT clock consumers.

Important APIs/types/functions: IDs cover fixed-rate oscillator/internal/free clocks, main/peripheral PLLs and outputs, MPU/boot/NOC/fixed-factor free clocks, S2F user clocks, EMAC free/PTP clocks, GPIO/SDMMC/PSI references, gated MPU/L4/CoreSight/timer/S2F/EMAC/GPIO/NAND/SDMMC/SPI/USB/NAND ECC clocks, and `AGILEX_NUM_CLKS`.

Control flow: DTS clock cells use these IDs; the Agilex clock driver registers providers and gates/dividers accordingly.

State and persistence: numeric values are DT ABI.

Dependencies and integration: standalone clock binding used by Agilex DTS and clock controller.

Risks and test signals: missing ID 42 and other gaps must be mirrored by provider tables. Test clock lookup for peripherals, CoreSight clocks, EMAC PTP, SDMMC, USB, and provider count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/agilex-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/alphascale,asm9260.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/alphascale,asm9260.h

Purpose: defines Alphascale ASM9260 clock IDs for AHB gates and system dividers.

Important APIs/types/functions: IDs cover AHB ROM/RAM/GPIO/MAC/EMI/USB/DMA/UART/I2S/I2C/SSP/IOCONFIG/WDT/CAN/MPWM/SPI/QEI/QuadSPI/camera/LCD/timers/IRQ/RTC/NAND/ADC/LED/DAC and system CPU/AHB/I2S/UART/SPI/QuadSPI/SSP/NAND/trace/camera/WDT/clkout/MAC/LCD/ADCANA dividers. `MAX_CLKS` is 74.

Control flow: DTS consumers use IDs; the ASM9260 clock driver maps them to gates/dividers.

State and persistence: constants are DT ABI.

Dependencies and integration: standalone clock binding for ASM9260.

Risks and test signals: `CLKID_SYS_UART3` and `CLKID_SYS_UART4` share value 56 in this header, so provider/consumer expectations must match that historical ABI. Test duplicate handling, UART clock lookup, and provider array bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/alphascale,asm9260.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/am3.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/am3.h

Purpose: defines TI AM3 clock-control register offsets as DT clock IDs for the clkctrl provider.

Important APIs/types/functions: base/index macros include `AM3_CLKCTRL_INDEX()` and per-domain variants for L4LS, L3S, L3, L4HS, PRUSS OCP, LCDC, 24MHz, L3 AON, and L4 WKUP AON. Constants identify UART, MMC, ELM, I2C, SPI, timers, RNG, GPIO, CAN, EPWMSS, spinlock, mailbox, OCPWP, USB OTG, GPMC, McASP, EMIF, AES, SHAM, TPCC/TPTC, PRUSS, CPSW, LCDC, control, ADC/TSC, SmartReflex, watchdog, debug, WKUP M3, MPU, RTC, GFX, and CEFUSE clkctrl offsets.

Control flow: DTS uses offset-derived IDs; TI clock drivers translate IDs back to register offsets relative to clkctrl blocks.

State and persistence: IDs are DT ABI and encode hardware register layout.

Dependencies and integration: standalone TI clock binding for AM33xx/AM3 SoCs.

Risks and test signals: wrong offset bases break register programming. Test clockctrl lookup, module enable/idle for each domain, suspend/resume, and DTS references against TRM offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/am3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/am4.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/am4.h

Purpose: defines TI AM4 clock-control register offset IDs for DT clkctrl consumers.

Important APIs/types/functions: macros derive IDs from offsets for global, L3S TSC, L4 WKUP AON, L4 WKUP, L3S, PRUSS OCP, L4LS, EMIF, DSS, and CPSW 125MHz domains. Constants cover ADC/TSC, WKUP M3, counter, timers, watchdog, I2C, UART, SmartReflex, control, GPIO, MPU, GFX, RTC, AES/DES/SHAM/TPCC/TPTC/L4HS, VPFE, GPMC, McASP, MMC, QSPI, USB OTG SS, PRUSS, CAN, EPWMSS, ELM, HDQ1W, mailbox, RNG, SPI, spinlock, UART, OCP2SCP, EMIF, DSS, and CPSW.

Control flow: clock-controller code uses the numeric IDs from DTS to select clkctrl registers and manage module clocks.

State and persistence: IDs encode stable hardware register offsets and are DT ABI.

Dependencies and integration: standalone AM4 clock binding.

Risks and test signals: offset arithmetic must match clock-driver base blocks. Test clkctrl registration, peripheral probe, low-power transitions, and schema references for every AM4 clock cell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/am4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,a1-peripherals-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,a1-peripherals-clkc.h

Purpose: defines Amlogic A1 peripheral clock controller IDs for DT consumers.

Important APIs/types/functions: IDs cover input roots, system/reset/analog/power/pad/sys controls, temperature sensor, AXI dividers, SPICC, measurement, audio/JTAG/SARADC/PWM/CEC/I2C/IR/ACODEC/OTP/SD/eMMC/USB, DSP, DMA, IRQ, NIC/GIC/UART/PSRAM/RSA/CoreSight, RAM/AXI gates, RTC/CEC 32K clocks, 24M/12M, generated clocks, SARADC/PWM/SPICC/TS/SPIFC/USB/SD/PSRAM/DMC mux/divider clocks, SYS/DSP mux/divider trees, and system PLL div16.

Control flow: DTS clock references map to A1 peripheral clock provider entries; the driver uses IDs to enable gates and configure mux/divider clocks.

State and persistence: IDs are stable DT ABI. Runtime rates/enables are held by the clock framework/provider.

Dependencies and integration: standalone Amlogic A1 clock binding.

Risks and test signals: numerous mux/divider/gate IDs must align with provider arrays. Test provider registration count, DTS reference lookup, clock enable for UART/I2C/PWM/USB/SD, and rate changes for generated clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,a1-peripherals-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,a1-pll-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,a1-pll-clkc.h

Purpose: defines Amlogic A1 PLL clock IDs for fixed PLL, fixed divisors, HIFI PLL, and SYS PLL.

Important APIs/types/functions: constants identify fixed PLL DCO/output, fixed clock divider nodes for div2/div3/div5/div7 and their outputs, HIFI PLL, and SYS PLL.

Control flow: DTS consumers reference PLL-derived clocks; the PLL clock controller registers DCOs, dividers, and outputs under these IDs.

State and persistence: IDs are DT ABI; runtime PLL rates and enable state live in the clock provider.

Dependencies and integration: standalone Amlogic A1 PLL binding.

Risks and test signals: provider and consumer ID mismatch can select wrong PLL roots. Test clock tree registration, fixed divisor rates, audio HIFI clock consumers, and CPU/system PLL dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,a1-pll-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,c3-peripherals-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,c3-peripherals-clkc.h

Purpose: defines Amlogic C3 peripheral clock controller IDs for system, AXI, media, display, storage, PWM, serial, and accelerator clocks.

Important APIs/types/functions: IDs cover RTC, reset/power/pad/sys controls, TS PLL, arbitration, MMC, CPU/JTAG/IR/IRQ/MSR/ROM/UART/RSA/SARADC/startup/secure/SPIFC/NNA/ETH/GIC/RAM/NIC/audio/PWM/USB/SD/SPICC/I2C/I2S/GE2D/ISP/MIPI/ETH PHY/ACODEC/DWAP/DOS/CVE/VOUT/VC9000E, AXI domains, 12/24M and FCLK clocks, generated clock, SARADC, PWM A-N selectors/dividers/outputs, SPICC, SPIFC, SD/eMMC A/B/C, TS, Ethernet, MIPI DSI, VOUT, codecs, VC9000E, CSI, DEWARPA, ISP, NNA, GE2D, and VAPB.

Control flow: clock consumers in DTS use these IDs; the C3 peripheral provider maps them to gates, muxes, dividers, and rate operations.

State and persistence: constants are DT ABI, while runtime state is clock-framework state.

Dependencies and integration: standalone Amlogic C3 peripheral clock binding.

Risks and test signals: large ID table alignment and media/display clock dependencies are risk areas. Test all DTS references, media/display probe, PWM outputs, Ethernet clocks, and provider count against max ID 200.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,c3-peripherals-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,c3-pll-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,c3-pll-clkc.h

Purpose: defines Amlogic C3 PLL clock IDs for fixed clocks, GP0, HIFI, MCLK PLL, and MCLK output trees.

Important APIs/types/functions: constants cover FCLK 50M, div2/div2.5/div3/div4/div5/div7 dividers and outputs, GP0 PLL DCO/output, HIFI PLL DCO/output, MCLK PLL DCO/OD/output, and MCLK0/MCLK1 selectors, enables, dividers, and outputs.

Control flow: DTS references select PLL roots and audio clocks; the C3 PLL provider registers and manages them.

State and persistence: DT ABI constants; PLL and divider runtime state belongs to the clock provider.

Dependencies and integration: standalone Amlogic C3 PLL binding.

Risks and test signals: audio MCLK and fixed divisor IDs are easy to confuse. Test rate calculations, MCLK0/MCLK1 consumers, and provider registration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,c3-pll-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,c3-scmi-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,c3-scmi-clkc.h

Purpose: defines Amlogic C3 SCMI clock IDs exposed through firmware.

Important APIs/types/functions: IDs cover DDR PLL/PHY, top/USB/MCLK/Ethernet/fixed/GP1 PLL oscillators, MIPIISP/VOUT, USB control, oscillator, system/AXI/CPU clocks, SYS PLL div16, and CPU div16.

Control flow: DTS consumers reference SCMI clock IDs; the SCMI clock protocol provider resolves them through firmware instead of direct MMIO clock control.

State and persistence: IDs are firmware/DT ABI. Runtime state is controlled by SCMI firmware.

Dependencies and integration: standalone C3 SCMI clock binding, integrated with SCMI clock drivers and Amlogic firmware.

Risks and test signals: firmware ID mismatch leads to unavailable or wrong clocks. Test SCMI discovery, DTS references, CPU/AXI/sys rate reporting, and firmware error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,c3-scmi-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,s4-peripherals-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,s4-peripherals-clkc.h

Purpose: defines Amlogic S4 peripheral clock controller IDs for RTC/CEC, system clocks, video/display, GPU/video decoders, storage, serial, PWM, security, audio, Ethernet, USB, and measurement clocks.

Important APIs/types/functions: IDs cover RTC and CEC 32K trees, sys clock A/B mux/dividers, smartcard, 12/24M, video PLL/VCLK trees, ENCI/ENCP/VDAC/HDMI, TS, Mali, VDEC/HEVC, VPU/VAPB/GE2D, VDIN, SD/eMMC, SPICC, PWM A-J, SARADC, generated clock, DDR/DOS/ETHPHY/MALI/AOCPU/AUCPU/CEC/NAND/smartcard/ACODEC/SPIFC/MSR/IR/audio/ETH/UART/I2C/HDMITX/HDCP22/MMC/RSA/GIC/demod/CDAC/ADC extclk and related selectors/dividers.

Control flow: DTS clock cells select S4 provider clocks for peripheral probe and media/display configuration.

State and persistence: constants are DT ABI.

Dependencies and integration: standalone Amlogic S4 peripheral binding.

Risks and test signals: media/display clock chains have many intermediate IDs, so provider ordering must match. Test HDMI/display modes, video decode, PWM, SD/eMMC, audio, Ethernet, HDCP22 clocks, and all DTS lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,s4-peripherals-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,s4-pll-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,s4-pll-clkc.h

Purpose: defines Amlogic S4 PLL clock IDs for fixed PLL divisors, GP0, HIFI, HDMI, and MPLL outputs.

Important APIs/types/functions: constants cover fixed PLL DCO/output, FCLK div2/div3/div4/div5/div7/div2.5 divider and output nodes, GP0 PLL, HIFI PLL, HDMI PLL DCO/OD/output, MPLL 50M, MPLL predivider, and MPLL0-3 dividers/outputs.

Control flow: DTS consumers and peripheral clock parents refer to these IDs; the PLL provider supplies rate/parent data.

State and persistence: IDs are DT ABI; runtime PLL state is provider-managed.

Dependencies and integration: standalone S4 PLL binding.

Risks and test signals: HDMI and audio PLL rate correctness is high impact. Test HDMI modes, audio clocks, FCLK divisor rates, and provider count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,s4-pll-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,t7-peripherals-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,t7-peripherals-clkc.h

Purpose: defines Amlogic T7 peripheral clock IDs for dualdiv RTC/CEC, DSPs, generated clocks, CSI/ISP, GPU, Ethernet, storage, serial, PWM, and system gates.

Important APIs/types/functions: IDs include RTC/CECA/CECB dualdiv trees, smartcard, DSPA/DSPB mux/dividers, 24M/12M/25M, Anakin clocks, TS, MIPI CSI/ISP, Mali, Ethernet RMII/125M, SD/eMMC, SPICC0-5, SARADC, PWM main and AO channels, and system gates for DDR/DOS/MIPI/ETHPHY/MALI/AOCPU/AUCPU/CEC/GDC/DESWARP/NAND/ETH/AXI/SD/eMMC/smartcard/ACODEC/SPIFC/MSR/IR/audio/UART/AIFIFO/PCIE/USB/I2C/HDMITX/HDMIRX/MMC/RSA/APB/DSP/VPU/SAR/GIC/thermal/PWM groups.

Control flow: DTS consumers use IDs to request clocks from the T7 peripheral provider; provider maps IDs to gates, muxes, dividers, and parents.

State and persistence: constants are DT ABI. Runtime state is provider/clock-framework state.

Dependencies and integration: standalone T7 peripheral clock binding.

Risks and test signals: new T7 table is broad and includes AO/main PWM and many system gates; provider ordering and DTS references are key. Test all referenced clocks, PCIe/USB/Ethernet/CSI/ISP/GPU/audio probes, and clock rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,t7-peripherals-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,t7-pll-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,t7-pll-clkc.h

Purpose: defines Amlogic T7 PLL clock IDs for several separate PLL providers or domains.

Important APIs/types/functions: the header groups IDs for GP0, GP1, HIFI, PCIE, MPLL, HDMI, and MCLK PLL families. Each group starts numbering at zero, defining domain-local IDs such as DCO/output pairs, PCIe OD/div2/output, MPLL prediv and MPLL0-3 outputs, HDMI DCO/OD/output, and MCLK selectors/dividers/outputs.

Control flow: compatible-specific PLL provider instances use the IDs for their own domain; DTS must include the appropriate provider node so overlapping numeric IDs are interpreted in the correct clock controller namespace.

State and persistence: constants are DT ABI within each provider namespace, not a single global table.

Dependencies and integration: standalone T7 PLL binding for Amlogic clock drivers.

Risks and test signals: overlapping IDs across groups are intentional but risky if a consumer references the wrong provider. Test each PLL provider instance, PCIe/HDMI/audio rate outputs, and DTS provider phandle correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,t7-pll-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,t7-scmi.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,t7-scmi.h

Purpose: defines Amlogic T7 SCMI firmware clock IDs.

Important APIs/types/functions: IDs cover DDR, audio, top, TCON, USB PLL0/1, MCLK, PCIe, Ethernet, PCIe refclk, EARC, SYS1, HDMI PLL oscillators, system/AXI clocks, fixed PLL and fixed divisors, FCLK 50M, CPU clock, A73 clock, and CPU/A73 div16 clocks.

Control flow: DTS references these IDs under an SCMI clock provider; the Linux SCMI clock driver asks firmware for rates/enables rather than touching MMIO directly.

State and persistence: IDs are firmware and DT ABI. Runtime clock state is owned by SCMI firmware.

Dependencies and integration: standalone T7 SCMI binding used by Amlogic firmware clock provider and device trees.

Risks and test signals: firmware/table mismatch can misreport CPU or bus clocks. Test SCMI enumeration, rate get/set where supported, CPU/A73 clocks, PLL oscillator availability, and firmware error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,t7-scmi.h -->
