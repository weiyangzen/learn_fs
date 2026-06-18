# subset-b-003597 research

Grouped research report for the Intel i915 display subset requested by `subset-b-003597`. Each file section is bounded with reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_setup.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_setup.c

Purpose: reads current display hardware state at driver load/resume and reconciles it into DRM atomic state, then sanitizes unsafe BIOS or firmware-programmed modeset state. It handles CRTCs, planes, encoders, connectors, power domains, DPLL state, watermarks, CDCLK, DBUF bandwidth, CMTG, FBC, VGA disable, PCH sanitize, DMC/vblank bring-up, and early display workarounds.

Important APIs/functions: `intel_modeset_setup_hw_state()` is the exported entry. Internal helpers include `intel_modeset_readout_hw_state()`, `intel_crtc_copy_hw_to_uapi_state()`, `intel_sanitize_encoder()`, `intel_sanitize_all_crtcs()`, `intel_crtc_disable_noatomic()`, `readout_plane_state()`, and `intel_modeset_update_connector_atomic_state()`. The noatomic disable path is split into begin/complete phases so joiner secondary pipes and port-sync slave/master pipes are disabled in a valid order.

Control flow: setup takes `POWER_DOMAIN_INIT`, applies early WA bits and disables VGA, reads CRTC pipe configs, planes, encoders, DPLLs, connectors, and derived clocks/bandwidths. It then acquires encoder power domains, sanitizes PCH/CMTG/fifo underrun reporting/vblank/FBC/plane mapping/encoders/connectors/CRTCs/DPLLs/watermarks, checks for leaked CRTC power-domain puts, drops the init wakeref, and sanitizes power domains. CRTC sanitization disables active pipes with no active encoders or TC links requiring reset; encoder sanitization can manually call disable/post_disable hooks when connectors are active but the pipe is not.

State and persistence: mutates live `drm_crtc_state`, `intel_crtc_state`, legacy connector encoder links, connector DPMS, `pmdemand` physical masks and port clocks, CRTC active/enabled flags, power domain references, and readout-derived inherited state. It intentionally marks states `inherited` so later commits fully recompute derived values.

Dependencies/integration: relies on atomic helpers, display power, DPLL, DDI/TC, FBC, DMC, vblank, watermarks, CDCLK, BW/DBUF, opregion notifications, PCH display, PM demand, and platform WA helpers. It is the bridge from firmware/BIOS state into the driver's atomic model.

Risks/test signals: fragile areas are noatomic disable ordering for joiner/port-sync, NULL atomic state passed to legacy encoder hooks, BIOS-bogus DPLL configs, TC HPD reset timing, connector reference balancing, and stale plane readout lacking full framebuffer state. Useful tests are boot/resume on systems with active BIOS displays, disconnected active Type-C ports, joiner/port-sync modes, LVDS/PCH encoders, DP MST avoidance, fifo underrun logs, WARNs from power-domain leakage, and state dumps after `setup_hw_state`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_setup.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_setup.h

Purpose: declares the modeset hardware-state setup entry point. It forward declares `struct drm_modeset_acquire_ctx` and `struct intel_display` to keep include dependencies small.

Important API: `void intel_modeset_setup_hw_state(struct intel_display *display, struct drm_modeset_acquire_ctx *ctx);` imports current hardware state, sanitizes it, and updates the driver's display state model.

Control flow/state: this header has no runtime state; callers supply a display object and an already relevant modeset acquire context used by the implementation when disabling inherited/broken CRTCs without going through a normal atomic userspace commit.

Dependencies/integration: consumed by display init/resume code that must reconcile firmware-programmed state before normal atomic commits and verification can run.

Risks/test signals: signature changes ripple into display bring-up. Build coverage across i915 and non-i915 display builds is the main header-level signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_verify.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_verify.c

Purpose: high-level display state verification after modeset/fastset activity. It cross-checks atomic software state, legacy connector/encoder links, hardware readout, DPLL state, PHY state, FDI dotclock assumptions, and watermark state.

Important functions: `intel_modeset_verify_crtc()` runs verification when a CRTC needs modeset or fastset. `intel_modeset_verify_disabled()` checks disabled encoders/connectors and DPLLs. Helpers include `verify_crtc_state()`, `verify_encoder_state()`, `verify_connector_state()`, `intel_connector_verify_state()`, and `intel_pipe_config_sanity_check()`.

Control flow: CRTC verification first verifies watermark state, then connector state for connectors targeting that CRTC, allocates a temporary CRTC state, reads hardware pipe config, compares active bits, checks encoder hardware state and pipe ownership, reads encoder config into the temporary state, runs FDI sanity, compares pipe config, dumps mismatched states, then verifies DPLL/MPLLB state. Disabled verification scans all encoders and connectors with old/new connector states and confirms no detached encoder is still enabled.

State and persistence: it should not persistently program hardware except through helper verification side effects; it allocates and destroys temporary CRTC state. It emits WARN-style diagnostics via `INTEL_DISPLAY_STATE_WARN()` and debug logs.

Dependencies/integration: depends on atomic state helpers, CRTC state allocation/readout/compare/dump, connector/encoder hooks, FDI link frequency, DPLL/MPLLB verification, and watermark verification.

Risks/test signals: false positives are possible where hardware readout is incomplete or platform exceptions exist, while false negatives hide state corruption. Exercise modeset, fastset, disabled encoder, PCH FDI, MST/non-MST, and PHY-specific paths with debug state checks enabled; look for `pipe state doesn't match`, encoder pipe mismatch, connector active/crtc mismatch, and DPLL verification warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_verify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_verify.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_verify.h

Purpose: exposes the modeset verification hooks used after atomic commits or when checking disabled state.

Important APIs: `intel_modeset_verify_crtc(struct intel_atomic_state *state, struct intel_crtc *crtc)` verifies active/changed CRTC state against hardware, while `intel_modeset_verify_disabled(struct intel_atomic_state *state)` validates disabled encoders/connectors/DPLLs.

Control flow/state: no local state. The interface deliberately accepts the full Intel atomic state because verification needs old/new connector state and CRTC-specific new state.

Dependencies/integration: included by commit tail or display verification paths; forward declarations avoid pulling in full atomic/CRTC definitions.

Risks/test signals: build failures or missing prototypes are the key header-level risk. Runtime validation belongs to the `.c` implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_verify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_opregion.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_opregion.c

Purpose: implements the Intel ACPI OpRegion bridge: mapping firmware mailboxes, handling SWSCI BIOS callbacks, ASLE interrupt work, ACPI video notification filtering, VBT/EDID extraction, adapter/encoder power notifications, headless SKU detection, and debugfs exposure of raw OpRegion memory.

Important types/functions: private packed mailbox structs model header, ACPI, SWSCI, ASLE, and ASLE extension layouts; `struct intel_opregion` stores mapped pointers, callback masks, VBT/RVDA pointers, work item, and ACPI notifier. Key APIs are `intel_opregion_setup()`, `intel_opregion_register()`, `intel_opregion_resume()/suspend()`, `intel_opregion_cleanup()`, `intel_opregion_notify_encoder()`, `intel_opregion_notify_adapter()`, `intel_opregion_get_edid()`, `intel_opregion_get_vbt()`, `intel_opregion_get_panel_type()`, and `intel_opregion_asle_intr()`.

Control flow: setup reads PCI `ASLS`, maps the 8 KiB region, validates signature, assigns mailbox pointers from the header bitmask, disables ACPI hotplug notifications via `chpd`, initializes SWSCI callback masks, marks ASLE not ready, then searches for VBT first via RVDA and then mailbox #4. Register installs the ACPI notifier and resumes the region. Resume populates DIDL/CADL, marks ACPI/ASLE ready, queries DSM support, and sends adapter D0. Suspend notifies adapter power state, marks ASLE not ready, cancels ASLE work, and clears ACPI readiness.

State and persistence: persistent driver state is `display->opregion`. Firmware-visible state includes `drdy`, `ardy`, `csts`, `chpd`, DIDL/CADL arrays, ASLE response bits, and current brightness `cblv`. RVDA and OpRegion mappings are held until cleanup. ASLE requests are processed asynchronously on `display->wq.unordered`.

Dependencies/integration: uses PCI config, ACPI notifier, DMI quirks, debugfs, DRM EDID helpers, backlight ACPI setter, ACPI device IDs, BIOS VBT validation, and display connector iteration. Modeset setup calls `intel_opregion_notify_encoder()` after encoder sanitization.

Risks/test signals: firmware mailboxes are platform-specific and often buggy. Watch SWSCI timeout/excessive delay paths, requested-vs-supported callback masks, DMI quirks for VBT/panel type, RVDA relative address handling, ASLE backlight lock coverage, notifier return values, and cleanup after failed setup. Tests should include ACPI-enabled and CONFIG_ACPI-off builds, invalid OpRegion signature, valid/invalid RVDA and mailbox VBTs, mailbox #5 EDID, suspend/resume readiness bits, ASLE backlight requests, and debugfs raw dump availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_opregion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_opregion.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_opregion.h

Purpose: public OpRegion interface for display code, with ACPI-enabled implementations and no-op stubs when `CONFIG_ACPI` is disabled.

Important APIs: setup/cleanup, register/unregister, resume/suspend, ASLE presence/interrupt, encoder and adapter notifications, panel type, EDID, VBT, headless SKU, and debugfs registration. The stubs return neutral values such as `0`, `false`, `NULL`, or `-ENODEV`.

Control flow/state: the header owns no state; it hides whether OpRegion support is compiled in. This lets display code call OpRegion helpers unconditionally where appropriate.

Dependencies/integration: depends on Linux PCI power-state types and display connector/encoder/display forward declarations. It is used by BIOS parsing, display init/resume, interrupt handling, modeset setup, and debugfs registration.

Risks/test signals: conditional-compilation mismatches can silently drop firmware integration. Build both ACPI and non-ACPI configurations, and verify callers handle `-ENODEV`/`NULL` fallback results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_opregion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_oprom_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_oprom_regs.h

Purpose: defines MMIO registers and bit masks for option ROM/SPI region access.

Important definitions: `PRIMARY_SPI_TRIGGER`, `PRIMARY_SPI_ADDRESS`, `PRIMARY_SPI_REGIONID`, `SPI_STATIC_REGIONS`, `OPTIONROM_SPI_REGIONID_MASK`, `OROM_OFFSET`, and `OROM_OFFSET_MASK`.

Control flow/state: no executable logic. The macros describe register offsets and fields used by option ROM discovery or reads elsewhere in the display/GPU code.

Dependencies/integration: depends on MMIO and register field helper macros from the display register infrastructure, though this tiny header itself only lists definitions.

Risks/test signals: the risk is incorrect register address or field mask, which would break option ROM access. Build coverage and hardware tests that read VBIOS/option ROM data are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_oprom_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_overlay.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_overlay.c

Purpose: implements the legacy Intel hardware overlay ioctl path. It validates userspace image and attribute requests, pins GEM buffers through parent callbacks, programs memory-backed overlay registers, handles scaling/polyphase coefficients, color key, brightness/contrast/saturation/gamma, and tracks which CRTC owns the overlay.

Important types/functions: `struct overlay_registers` mirrors the overlay command/register page; `struct intel_overlay` stores display, CRTC, pfit state, color key, image attributes, previous scales, and MMIO/register pointer. Public APIs are `intel_overlay_setup()`, `intel_overlay_available()`, `intel_overlay_cleanup()`, `intel_overlay_reset()`, `intel_overlay_switch_off()`, `intel_overlay_put_image_ioctl()`, and `intel_overlay_attrs_ioctl()`. Core helpers validate source/destination/scaling and program registers in `intel_overlay_do_put_image()`.

Control flow: setup allocates the overlay, obtains parent overlay register storage, clears it, loads static polyphase coefficients, and writes default attributes. `put_image` handles disable requests, finds the target CRTC and GEM object, locks modeset globally, recovers pending overlay interrupts, switches CRTC ownership if needed, validates destination within pipe source, compensates for active pfit vertical scaling, validates source geometry/strides/offsets/object bounds and scaling ratio, then pins and programs buffer offsets, strides, dimensions, scale registers, color key, command bits, and frontbuffer continuation. Switch-off recovers, releases old video, clears `OCMD`, unlinks CRTC, and calls parent off.

State and persistence: persistent state is `display->overlay`, `overlay->crtc`, `crtc->overlay`, default/current image attributes, cached scale ratios, and parent-managed pinned overlay buffers. It increments/decrements `display->restore.pending_fb_pin` around pinning and relies on parent overlay code for active/old-video state.

Dependencies/integration: integrates with DRM ioctls, GEM lookup, display parent overlay operations, frontbuffer tracking, pfit registers, primary plane framebuffer format for color key conversion, and global modeset locking.

Risks/test signals: legacy overlay hardware can hang on bad limits, so validation is central. Risk areas include signed brightness assigned to `u32`, mutation of user parameter struct for pfit compensation, object-bound overflow assumptions, CRTC switch cleanup, gamma updates while active, and parent callback availability. Test with packed/planar YUV formats, invalid strides/offsets/sizes, scaling >8x down, inactive/double-wide CRTC, pfit active modes, gamma errata values, repeated on/off, interrupt recovery, and suspend/reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_overlay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_overlay.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_overlay.h

Purpose: declares the legacy overlay lifecycle and ioctl entry points.

Important APIs: setup/availability/cleanup/reset, `intel_overlay_switch_off()`, `intel_overlay_put_image_ioctl()`, and `intel_overlay_attrs_ioctl()`.

Control flow/state: no state in the header. It exposes `struct intel_overlay` opaquely so callers can switch off without seeing internal register/attribute fields.

Dependencies/integration: used by display init/cleanup, parent wrappers, and DRM ioctl dispatch. Includes Linux types and forward declarations for DRM device/file and Intel display structs.

Risks/test signals: header risk is ABI mismatch with ioctl dispatch or missing CONFIG coverage. Build and ioctl smoke tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_overlay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_panel.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_panel.c

Purpose: centralizes embedded panel fixed-mode management, panel mode validation/configuration, DRRS/VRR fixed-mode selection, EDID/VBT/current-mode fixed-mode ingestion, panel/backlight lifetime, connector detection, and DRM panel follower preparation.

Important functions: `intel_panel_use_ssc()`, `intel_panel_preferred_fixed_mode()`, `intel_panel_fixed_mode()`, `intel_panel_downclock_mode()`, `intel_panel_highest_mode()`, `intel_panel_get_modes()`, `intel_panel_compute_config()`, `intel_panel_add_edid_fixed_modes()`, VBT/current fixed-mode adders, `intel_panel_detect()`, `intel_panel_mode_valid()`, `intel_panel_init_alloc()`, `intel_panel_init()`, `intel_panel_fini()`, `intel_panel_register()/unregister()`, and `intel_panel_prepare()/unprepare()`.

Control flow: initialization seeds VBT defaults and fixed mode list, then later stores fixed EDID, initializes backlight functions, and disables DRRS if no matching alternate fixed modes exist. EDID modes are reduced to preferred and optional alternate fixed modes; VBT/current modes are duplicated and added as preferred driver modes. Compute config chooses the best fixed mode for requested refresh, rejects non-VRR refresh mismatches beyond 1 Hz, copies fixed timings, and for VRR adjusts `vtotal` to match requested refresh. Registration creates a backlight device and, for eDP/DSI, allocates/registers a DRM panel once the connector kdev exists, then syncs already-enabled panel state.

State and persistence: `connector->panel` owns fixed EDID, fixed mode list, VBT-derived panel fields, backlight state, and optional `drm_panel *base`. Probed EDID modes are moved/destroyed after fixed-mode extraction.

Dependencies/integration: integrates with DRM mode lists, EDID helpers, backlight, VBT/BIOS parsing, quirks, DRRS, VRR, connector sysfs/kdev lifecycle, ACPI fwnodes, and DRM panel follower notifications.

Risks/test signals: important risks are mode list ownership, fixed EDID lifetime, VRR vtotal math, 1 Hz tolerance behavior, DRRS detection, panel registration after kdev creation, and prepare sync for BIOS-enabled panels. Test eDP/DSI/LVDS connectors with EDID preferred/alternate modes, VBT fallback, current BIOS mode fallback, VRR refresh requests, DRRS downclock modes, backlight registration failure, late_register panel sync, and unregister/fini cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_panel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_panel.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_panel.h

Purpose: exposes panel fixed-mode, detection, configuration, backlight/panel lifecycle, and panel follower notification APIs.

Important APIs: fixed mode selectors (`preferred`, `fixed`, `downclock`, `highest`), `intel_panel_get_modes()`, `intel_panel_drrs_type()`, `intel_panel_mode_valid()`, `intel_panel_compute_config()`, EDID/VBT/current fixed-mode adders, init/fini/register/unregister, detect, SSC choice, prepare/unprepare.

Control flow/state: no implementation state. The signatures make callers pass connectors, CRTC state, connector state, and encoders as needed for panel decisions and lifecycle.

Dependencies/integration: used by LVDS/eDP/DSI/backlight/BIOS code. Forward declarations keep compile dependencies low.

Risks/test signals: API behavior is tightly coupled to connector panel ownership and mode-list lifetimes. Header changes require broad display build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_panel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_parent.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_parent.c

Purpose: provides typed convenience wrappers from display code to the generic parent interface in `display->parent`. It adapts display-driver types to parent callbacks for DPT, frontbuffer, HDCP GSC, IRQ, overlay, panic, PC8, pcode, RPS, stolen memory, VMA, and generic feature queries.

Important functions: wrappers are named `intel_parent_<subsystem>_<operation>()`, such as `intel_parent_overlay_pin_fb()`, `intel_parent_stolen_insert_node()`, `intel_parent_pcode_request()`, `intel_parent_hdcp_gsc_msg_send()`, and `intel_parent_irq_synchronize()`. Several functions guard optional subinterfaces with `if` checks or `drm_WARN_ON_ONCE()`, while many mandatory callbacks are called directly.

Control flow: most functions immediately dispatch to `display->parent->...` with `display->drm` or translated object pointers. Optional subsystems return neutral values (`NULL`, `false`, `-1`, `0`, `-ENODEV`) or no-op when unavailable. Overlay wrappers are used by the legacy overlay implementation to isolate GEM/VMA/frontbuffer details outside display.

State and persistence: this file owns no state; all persistence is in parent subsystems and objects passed through callbacks. It can affect parent-managed references, pinned buffers, stolen-memory nodes, pcode mailbox transactions, and power-management blocks through delegated calls.

Dependencies/integration: depends on `drm/intel/display_parent_interface.h` and `intel_display_core.h`. It is an integration boundary between i915 display code and the parent GPU driver/services.

Risks/test signals: direct dereferences assume mandatory parent subinterfaces exist; optional checks must match real platform capabilities. Tests should cover configurations lacking optional RPS/VMA/overlay/PC8/stolen callbacks, overlay pin/unpin failure paths, pcode timeout behavior, HDCP GSC allocation/free, and stolen-memory allocation/free symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_parent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_parent.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_parent.h

Purpose: declares typed display-to-parent wrapper APIs for shared services outside the display core.

Important APIs: DPT create/destroy/suspend/resume; frontbuffer get/ref/put/flush; HDCP GSC messaging/context; IRQ enabled/synchronize; overlay lifecycle/pin/object lookup; panic setup; PC8 block/unblock; pcode read/write/request; RPS helpers; stolen memory insert/remove/query/node allocation; VMA fence id; AUX CCS/fenced-region/vGPU queries; display fence priority.

Control flow/state: no state. The broad API mirrors parent interface capabilities while keeping display code independent of the raw parent function table.

Dependencies/integration: included by overlay, HDCP, stolen-memory, DPT, power, and display support code. Forward declarations keep it decoupled from concrete parent implementations.

Risks/test signals: wrapper signatures must stay synchronized with `display_parent_interface`. Build failures catch many mismatches; runtime tests should cover optional-parent absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_parent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch.c

Purpose: detects the platform controller hub/south display compatibility type and applies PCH-specific clock-gating workarounds.

Important functions: `intel_pch_detect()` scans ISA bridge PCI devices or synthesizes fake/no-display PCH types, `intel_pch_init_clock_gating()` dispatches workarounds, `intel_pch_type()` maps masked PCI IDs to `enum intel_pch`, `intel_pch_fake_for_south_display()` handles DG1/DG2/MTL/LNL-style integrated south display, and virtualization helpers recognize QEMU/virt PCH cases.

Control flow: detection first checks fake south-display platforms; otherwise it scans Intel ISA bridges, masks device IDs, maps them to PCH types, and handles virtual/emulated bridges by estimating from GPU platform. If display is disabled, a detected PCH becomes `PCH_NOP`; if no bridge is found but running as a guest with display, it estimates a virtual PCH. Clock-gating init applies IBX/CPT/LPT/CNP register workarounds including panel power sequencer, chicken bits, FDI polarity, DP unit gating, LPT LP partition disable, and CNP PWM gating.

State and persistence: stores the result in `display->pch_type`; writes persistent hardware workaround bits in south display registers.

Dependencies/integration: uses PCI class scanning, display platform flags, VBT FDI RX polarity, display MMIO helpers, register definitions, guest detection, and the public `enum intel_pch`/macros from `intel_pch.h`.

Risks/test signals: mapping errors affect many south-display paths. Watch WARNs that platform generation does not match PCH ID, virtualization assumptions, fake PCH selection for new discrete/integrated platforms, and clock-gating bits on old LVDS/PCH systems. Test native and passthrough VMs, no-display SKUs, IBX/CPT/LPT/CNP hardware, and DG/MTL/LNL fake-PCH platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch.h

Purpose: defines PCH compatibility categories and helper macros used throughout display code.

Important types/macros: `enum intel_pch` is ordered by south display compatibility and includes real PCHs (`IBX` through `ADP`), `PCH_NOP`, `PCH_NONE`, and fake PCHs for DG1/DG2/MTL/LNL. Macros like `HAS_PCH_LPT()`, `HAS_PCH_SPLIT()`, and `INTEL_PCH_TYPE()` centralize checks.

Control flow/state: no runtime logic beyond macro evaluation against `display->pch_type`. Declares `intel_pch_detect()` and `intel_pch_init_clock_gating()`.

Dependencies/integration: included by PCH display/refclk/backlight/LVDS and platform-specific display code.

Risks/test signals: enum ordering and compatibility comments matter because many checks imply inherited south display behavior. Build and platform boot tests catch misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_display.c

Purpose: manages split PCH display resources: PCH transcoders, FDI link enable/disable sequencing, PCH DPLL selection, PCH transcoder timings/M/N values, PCH DP transcoding bits, LPT iCLKIP path, PCH config readout, and IBX port sanitization.

Important functions: `intel_has_pch_trancoder()`, `intel_crtc_pch_transcoder()`, `ilk_pch_pre_enable()`, `ilk_pch_enable()`, `ilk_pch_disable()`, `ilk_pch_post_disable()`, `ilk_pch_get_config()`, `lpt_pch_enable()`, `lpt_pch_disable()`, `lpt_pch_get_config()`, M/N get/set helpers, and `intel_pch_sanitize()`.

Control flow: ILK/CPT enabling starts FDI PLL before CPU pipe enable, then trains FDI, selects PCH DPLL, enables DPLL, programs PCH M/N and timings copied from CPU transcoder, performs normal FDI train, optionally configures CPT `TRANS_DP_CTL`, and enables the PCH transcoder. Disable tears down FDI, disables PCH transcoder, clears DP/DPLL select bits, disables FDI PLL, and drops DPLL. LPT uses fixed PCH transcoder A, programs iCLKIP, copies timings, enables/disables LPT transcoder, and disables iCLKIP on teardown. Config readout detects active PCH transcoders, reads FDI lanes/M/N, DPLL state or iCLKIP clock, and sets `has_pch_encoder`.

State and persistence: programs PCH transcoder registers, FDI RX/TX dependencies, DPLL selection, DP transcoding control, timings, and `crtc_state` readout fields. Sanitization rewrites stale IBX disabled-port transcoder select bits to pipe A to avoid false asserts.

Dependencies/integration: depends on CRT/LVDS/SDVO/DP port helpers, FDI, DPLL, PPS unlock asserts, PCH refclk, register helpers, and atomic CRTC state.

Risks/test signals: sequencing is hardware-sensitive. Test PCH LVDS/HDMI/DP/CRT paths on IBX/CPT/LPT, FDI training failures, DPLL sharing, interlaced modes, DP M/N readback, LPT iCLKIP clock readback, and asserts for ports/transcoder disabled during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_display.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_display.h

Purpose: declares PCH transcoder/display sequencing APIs and provides inert stubs when `I915` is not defined.

Important APIs: PCH transcoder availability/mapping; ILK pre-enable/enable/disable/post-disable/get-config; LPT enable/disable/get-config; PCH transcoder M/N getters; `intel_pch_sanitize()`.

Control flow/state: no state. The stubs make non-i915 builds compile while returning false/zero or no-op.

Dependencies/integration: consumed by encoder/CRTC enable and readout paths for PCH-backed outputs.

Risks/test signals: prototype or stub return type mismatch can break alternate builds. Hardware sequencing coverage belongs to the `.c` implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_refclk.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_refclk.c

Purpose: initializes and controls PCH reference clocks for IBX/CPT and LPT platforms, including LPT iCLKIP programming, CLKOUT_DP enable/disable, SSC source decisions, and Haswell FDI mPHY programming workaround.

Important functions/types: `struct iclkip_params` captures divisor/phase settings. Public APIs are `lpt_program_iclkip()`, `lpt_disable_iclkip()`, `lpt_get_iclkip()`, `lpt_iclkip()`, `lpt_disable_clkout_dp()`, and `intel_init_pch_refclk()`. Important helpers include `lpt_compute_iclkip()`, `lpt_enable_clkout_dp()`, `lpt_bend_clkout_dp()`, `spll_uses_pch_ssc()`, `wrpll_uses_pch_ssc()`, `lpt_init_pch_refclk()`, and `ilk_init_pch_refclk()`.

Control flow: LPT iCLKIP programming disables the clock, computes divisors from adjusted mode clock, writes SBI ICLK divider/phase/auxdiv/control registers under SBI lock, waits 24 us, then ungates pixel clock. LPT refclk init checks whether SPLL/WRPLLs already use PCH SSC; if so it preserves it, otherwise enables CLKOUT_DP with FDI if analog output exists or disables it. ILK/CPT init inspects encoders for LVDS/eDP/panel, checks active DPLLs using SSC, computes final `PCH_DREF_CONTROL`, and transitions nonspread/SSC/CPU outputs with required delays.

State and persistence: writes SBI ICLK/MPHY registers, `PIXCLK_GATE`, `PCH_DREF_CONTROL`, and tracks `display->dpll.pch_ssc_use` bitmask. It may leave PCH SSC enabled to avoid disrupting active PLL users.

Dependencies/integration: uses encoder list, panel SSC policy, platform/PCH macros, DPLL lists, SBI lock/read/write, display MMIO, and PCH display LPT paths.

Risks/test signals: reference clock transitions are timing-sensitive and platform-specific. Test LPT-H vs LPT-LP, analog FDI present/absent, CPU eDP/LVDS panel SSC choices, CK505 systems, active PLLs already using PCH SSC, runtime suspend/resume, and exact iCLKIP frequency readback. Watch WARNs for FDI without spread, invalid clock divisors, and LP PCH FDI assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_refclk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_refclk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_refclk.h

Purpose: declares PCH reference clock control APIs and provides no-op stubs for non-I915 builds.

Important APIs: LPT iCLKIP program/disable/get/compute, global PCH refclk init, and LPT CLKOUT_DP disable.

Control flow/state: no state. Stub implementations return `0` or no-op, allowing shared code to compile when i915-specific PCH refclk logic is unavailable.

Dependencies/integration: used by PCH display enable/disable and display initialization.

Risks/test signals: header-level risks are conditional compilation and call-site assumptions about nonzero clock returns. Build both I915 and stub configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_refclk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pfit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pfit.c

Purpose: computes, validates, programs, disables, and reads back panel fitter/scaler state for GMCH-era and PCH/CPU panel fitters.

Important functions: `intel_pfit_compute_config()`, `intel_pfit_mode_valid()`, `ilk_pfit_enable()/disable()/get_config()`, `i9xx_pfit_enable()/disable()/get_config()`. Helpers compute PCH destination windows, source-size/scaling/timing/cloning validity, GMCH centering/aspect/fullscreen scaling, programmed ratios, and legacy timing limits.

Control flow: `intel_pfit_compute_config()` dispatches to GMCH or PCH. PCH fitting compares pipe source to fixed adjusted mode, computes destination window from connector scaling mode, sets `crtc_state->pch_pfit`, and for pre-SKL validates centered window, source size, max downscaling, timings, and no cloning. GMCH fitting modifies adjusted CRTC timings for centered/aspect modes where needed, computes PFIT control/ratio/border bits, rejects unsupported downscaling, and stores `gmch_pfit` fields. Enable paths program PF/PFIT registers only when state says fitting is enabled; disable paths clear them with required pipe-disabled assertions for GMCH.

State and persistence: mutates `intel_crtc_state` fields `pch_pfit` and `gmch_pfit`, sometimes modifies adjusted mode timings, and writes PFIT/PF window/control/ratio/border registers during enable/disable. Readout populates those fields from hardware registers.

Dependencies/integration: uses connector scaling mode, DRM rect/mode helpers, display version/platform checks, LVDS border registers, PCH/CPU pfit registers, SKL scaler mode validation, and transcoder-disabled asserts.

Risks/test signals: risks include off-by-one centering, interlace alignment, downscale limits, cloning rejection, DISPLAY_VER-specific max source sizes, IVB/HSW pipe selection readout, and modifying adjusted mode for GMCH. Test all scaling modes, native/no-fit, aspect pillar/letter, centered modes, YCbCr420 pfit use, interlaced modes, cloned outputs, pre-965/965+/ILK/IVB/HSW/SKL+ platforms, and pfit readout after BIOS-enabled panels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pfit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pfit.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pfit.h

Purpose: declares panel fitter compute, validation, programming, disable, and readout APIs.

Important APIs: `intel_pfit_compute_config()`, `intel_pfit_mode_valid()`, ILK/PCH enable-disable-readout, and i9xx/GMCH enable-disable-readout.

Control flow/state: no state; functions operate on `intel_crtc_state`, connector state, display, and display modes to store or apply pfit decisions.

Dependencies/integration: used by LVDS/eDP/CRTC modeset computation and enable/disable/readout paths.

Risks/test signals: signatures must stay aligned with CRTC state fields and scaler validation. Build coverage and scaling-mode tests catch regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pfit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pfit_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pfit_regs.h

Purpose: register definitions for legacy GMCH panel fitter and CPU/PCH panel fitter windows, controls, scaling ratios, and filter fields.

Important definitions: `PFIT_CONTROL`, `PFIT_ENABLE`, pipe/scaling/filter/interpolation/auto-scale/dither fields; `PFIT_PGM_RATIOS` and `PFIT_AUTO_RATIOS`; `PF_CTL`, `PF_WIN_SZ`, `PF_WIN_POS`, `PF_VSCALE`, and `PF_HSCALE` with size/position/filter/pipe-select fields.

Control flow/state: no executable logic. These macros are used by pfit compute/program/readout code and overlay pfit compensation.

Dependencies/integration: depends on `intel_display_reg_defs.h` MMIO and bitfield helpers. Integrated by `intel_pfit.c`, overlay, LVDS, and display readout paths.

Risks/test signals: wrong masks or register offsets cause broken scaling or readout. Note `PF_FILTER_EDGE_ENHANCE/SOFTEN` reference `PF_FILTER_EDGE_MASK`, which is not defined in this header and should be checked by compile coverage. Hardware tests should verify programmed pfit windows and scaling ratios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pfit_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pipe_crc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pipe_crc.c

Purpose: implements debugfs/DRM CRTC CRC source selection and pipe CRC enable/disable for many display generations. It translates source names into generation-specific `PIPE_CRC_CTL` bits, validates supported sources, applies workarounds, and synchronizes IRQ teardown.

Important functions: `intel_crtc_crc_init()`, `intel_crtc_get_crc_sources()`, `intel_crtc_verify_crc_source()`, `intel_crtc_set_crc_source()`, `intel_crtc_enable_pipe_crc()`, and `intel_crtc_disable_pipe_crc()`. Generation helpers include i8xx/i9xx/VLV/ILK/IVB/SKL source validation and control-register builders, `i9xx_pipe_crc_auto_source()`, `vlv_undo_pipe_scramble_reset()`, and `intel_crtc_crc_setup_workarounds()`.

Control flow: source strings map to `enum intel_pipe_crc_source`; verification checks whether a source is valid for the platform and reports five CRC values. Setting a source obtains the pipe power domain if enabled, enables CRC-related workarounds when turning CRC on, builds the generation-specific control word, writes `PIPE_CRC_CTL`, resets skipped count, undoes VLV scramble reset on disable, disables workarounds when turning off, and drops the wakeref. Enable/disable functions support modeset transitions when the debugfs CRC file is open; disable sets `skipped = INT_MIN`, clears the register, posting reads, and synchronizes parent IRQs.

State and persistence: initializes and uses `crtc->pipe_crc.lock`, `source`, and `skipped`. It writes PIPE CRC MMIO, VLV/G4X symbol reset bits, and may commit internal atomic state to toggle PSR/CRC workarounds.

Dependencies/integration: depends on debugfs CRC hooks in `intel_crtc`, display power domains, display IRQ handlers, parent IRQ sync, atomic commits, PSR state, platform register definitions, DP/TV encoder inspection, and modeset locks for auto-source detection.

Risks/test signals: risks include enabling CRC while pipe off, auto-source with concurrent modesets, generation-specific unsupported tap points, VLV scramble reset cleanup, workaround atomic commit deadlocks, and IRQs arriving after disable. Test debugfs CRC on gen2, gen3/4 TV, VLV/CHV DP, ILK/SNB, IVB/HSW, and SKL+ plane sources; include source `auto`, invalid source names, pipe-off error, PSR-enabled panels, and open CRC across modesets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pipe_crc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pipe_crc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pipe_crc.h

Purpose: exposes pipe CRC debugfs hooks, with null/no-op stubs when `CONFIG_DEBUG_FS` is disabled.

Important APIs: CRC init, set source, verify source, get source list, enable pipe CRC, and disable pipe CRC. Stub mode maps DRM CRC function pointers to `NULL` and lifecycle calls to no-ops.

Control flow/state: no local state. The compile-time split allows CRTC setup code to assign debugfs CRC callbacks only when supported.

Dependencies/integration: used by `intel_crtc.c`, IRQ/modeset paths, and CRC debugfs support.

Risks/test signals: debugfs-off builds must not dereference absent callbacks. Build with and without `CONFIG_DEBUG_FS`; runtime tests belong to `intel_pipe_crc.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pipe_crc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pipe_crc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pipe_crc_regs.h

Purpose: defines pipe CRC control, expected-value, and result registers across Intel display generations.

Important definitions: `PIPE_CRC_CTL()` and `PIPE_CRC_ENABLE`; source-selection masks and values for SKL+, IVB+, ILK+, VLV, i9xx/G4X, and gen2 border inclusion; pre-IVB expected/result channel registers; IVB expected/result registers; HSW expected/result registers.

Control flow/state: no logic. The macros encode MMIO offsets and bitfields used by CRC setup and IRQ handlers.

Dependencies/integration: depends on `intel_display_reg_defs.h` and is consumed by `intel_pipe_crc.c` plus display IRQ CRC handlers that read result registers.

Risks/test signals: register aliasing mistakes can produce bad CRC values. Notably `PIPE_CRC_EXP_4_IVB()` and `PIPE_CRC_EXP_5_IVB()` use `_PIPE_CRC_EXP_2_*` in the macro body despite defining separate offsets nearby; this deserves compile/source review against hardware specs. Test CRC capture on IVB/HSW/SKL and compare expected result register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pipe_crc_regs.h -->
