# subset-b-003771 research

This grouped report covers the requested Xe GuC ABI, i915 compatibility, display integration, instruction encoding, and register-definition files. Each file section is source-tree-aligned and intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_actions_sriov_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_actions_sriov_abi.h

Purpose: defines the GuC SR-IOV action ABI used between PF, VF, and GuC firmware. It is a wire-format header, not executable code. Important APIs are action IDs and message length/field macros for relay forwarding, adverse events, VF state notifications, VF version matching, VGT policy updates, VF provisioning, VF control, VF reset, KLV query, migration save/restore, and RESFIX start/done. Control flow is encoded as expected HXG request/event/response sequences over CTB or MMIO. State persistence is external: GuC owns VF lifecycle/configuration state and the driver passes GGTT addresses, VFIDs, sizes, markers, and KLV buffers. Dependencies include `guc_communication_ctb_abi.h`, HXG macros, relay payload limits, and KLV definitions. Integration points are PF/VF SR-IOV management, migration recovery, and VF provisioning. Risks are malformed lengths, wrong transport selection, nonzero/zero marker compatibility around VF ABI 1.27.0, and command macros that use event length names for request messages. Test signals include ABI packing/field extraction tests, PF/VF relay selftests, version negotiation, invalid VFID handling, migration save/restore buffer bounds, and firmware response-code coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_actions_sriov_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_capture_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_capture_abi.h

Purpose: describes GuC register capture lists and error-state capture records. Important types are `guc_mmio_reg`, `guc_mmio_reg_set`, `guc_debug_capture_list`, `guc_state_capture_t`, and `guc_state_capture_group_t`, plus enums for PF/VF list index, global/class/instance capture type, engine class, and full/partial group type. Control flow is data-driven: the host registers capture lists in ADS, then GuC logs captured MMIO entries before reset or fault handling. State is packed firmware-shared memory with flexible arrays and bitfields for VFID, engine class/instance, LRCA, GuC context id, steering, masks, and entry counts. Dependencies are Linux integer types and bit macros. Integration is with GuC log parsing, engine reset diagnostics, SR-IOV owner attribution, and register restore/capture programming. Risks include packed layout drift, count overrun, wrong steering fields, and confusing `restore only` or `masked with value` semantics. Test signals include structure size/layout checks, parser fuzzing for flexible arrays, SR-IOV owner tests, and captured register count validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_capture_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_communication_ctb_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_communication_ctb_abi.h

Purpose: defines command transport buffer communication between host and GuC. Important types and macros include `struct guc_ct_buffer_desc`, `GUC_CTB_STATUS_*`, CTB header length, `FENCE`, `FORMAT`, `NUM_DWORDS`, `GUC_CTB_FORMAT_HXG`, and min/max CTB HXG lengths. Control flow is a producer/consumer ring: sender advances tail, receiver advances head, and status reports overflow, underflow, mismatch, or disabled state. State lives in a 64-byte packed descriptor plus one-direction circular buffers shared with firmware. Dependencies include `guc_messages_abi.h` and `static_assert` for descriptor size. Integration points are H2G/G2H CT channels, SR-IOV relay payload sizing, and any GuC action transported after early MMIO setup. Risks include head/tail unit confusion, wrap handling, descriptor tampering detection, and exceeding the 255 dword CTB payload limit. Test signals include descriptor size assertions, ring wrap tests, malformed length rejection, and CTB status recovery tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_communication_ctb_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_communication_mmio_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_communication_mmio_abi.h

Purpose: documents early GuC MMIO communication through scratch registers. The only concrete API is `GUC_MAX_MMIO_MSG_LEN`, fixed at four dwords. Control flow is direct register write/read of HXG messages before CTB channels are configured; the header notes Gen9 legacy scratch registers and Gen11 preferred registers. State is transient in hardware scratch registers, not persistent memory. Dependencies are conceptual rather than included: HXG format and platform register definitions. Integration points are early driver initialization, VF version matching, VF reset, RESFIX start/done, and single KLV query actions that must use MMIO transport. Risks include using CTB-only messages over MMIO, assuming more than four dwords are available, and platform register selection errors. Test signals are early GuC boot paths, MMIO action length checks, scratch register selection per generation, and fallback/error handling before CTB availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_communication_mmio_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_errors_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_errors_abi.h

Purpose: centralizes numeric GuC response, load status, and bootrom status constants. Important APIs are the `xe_guc_response`, `xe_guc_load_status`, and `xe_bootrom_load_status` enums. Control flow is external: command senders receive HXG failure codes or load-status register values and map them to driver diagnostics or retry decisions. State is firmware-owned status codes, including protocol, permission, KLV, CTB, VF, decryption, hardware timeout, and generic failure categories. Dependencies are minimal and there are no functions. Integration points are GuC command transport, firmware load, bootrom authentication, SR-IOV authorization, and log messages. Risks include stale numeric values versus firmware, duplicate or typo-prone constants such as uppercase `0X101`, and treating retryable/pending states as fatal. Test signals include error-code string tables, firmware load failure injection, HXG failure parsing, and negative tests for KLV, CTB, and VF provisioning paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_errors_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_klvs_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_klvs_abi.h

Purpose: defines the GuC key-length-value ABI for self configuration, global configuration, scheduling policies, VGT policy, VF provisioning, opt-in features, and GuC workarounds. Important APIs are `GUC_KLV_0_KEY`, `GUC_KLV_0_LEN`, the self-config CTB/memory IRQ keys, context policy IDs, opt-in feature keys, render/compute yield policy, VGT scheduling group policy, VF resource/time-slice/adverse-threshold keys, and `enum xe_guc_klv_ids` workaround keys. Control flow is buffer based: the driver builds KLV arrays, passes addresses through GuC action messages, and GuC applies or rejects entries. State persists in firmware configuration and VF scheduling/provisioning state. Dependencies include `guc_scheduler_abi.h` for engine class/group limits. Integration points include `HOST2GUC_SELF_CFG`, `PF2GUC_UPDATE_VGT_POLICY`, `PF2GUC_UPDATE_VF_CFG`, scheduler policy updates, and workaround programming. Risks include key length mismatch, group arrays shorter than firmware expectations, clamped timeouts, nonzero tile masks, and version-gated features. Test signals include KLV encoder/decoder tests, max/min length checks, firmware compatibility gates, VF resource provisioning tests, and malformed KLV rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_klvs_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_lfd_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_lfd_abi.h

Purpose: defines the GuC log file descriptor stream format used to package firmware and KMD log metadata and payloads. Important APIs are format version macros, `enum guc_lfd_type`, `enum guc_lfd_os_type`, `struct guc_lfd_data`, `struct guc_lfd_data_log_events_buf`, `struct guc_lfd_data_os_info`, and `struct guc_lfd_file_header`. Control flow is append/parse of typed LFD blocks under a file header. State is persisted in generated log files, with firmware-required descriptors for version/device/timestamp/GMD/build platform and optional firmware/KMD descriptors for event buffers, crash dumps, binary schema, comments, and timestamp anchors. Dependencies include `guc_lic_abi.h` and Linux counted flexible-array annotations. Integration points are GuC log streaming, crash collection, host tooling, and timestamp correlation. Risks include miscomputed dword counts, bad magic/type extraction, string alignment, and optional descriptor compatibility. Test signals include file parser round trips, required descriptor presence, OS info padding tests, and malformed stream rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_lfd_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_lic_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_lic_abi.h

Purpose: defines the GuC log-init-config block written by firmware into log buffer memory. Important APIs are `enum guc_lic_type`, `struct guc_lic`, `GUC_LIC_MAGIC`, and major/minor version masks. Control flow is simple producer/consumer: GuC populates the packed header and KLV data at log init time, then KMD validates and consumes it. State is persistent within the log buffer allocation and carries firmware version, device id, timestamp frequency, GMD ID, and build platform ID. Dependencies are Linux types and GENMASK macros. Integration points include GuC log setup, LFD generation, timestamp conversion, and diagnostics. Risks include accepting invalid magic, version drift, truncated flexible arrays, and interpreting LIC data without KLV length validation. Test signals include magic/version validation, required key parsing, truncated buffer tests, and cross-checks with firmware load metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_lic_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_log_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_log_abi.h

Purpose: describes GuC log buffer layout and per-buffer coordination state. Important APIs are `enum guc_log_type`, `GUC_LOG_BUFFER_TYPE_MAX`, `struct guc_log_buffer_state`, and flag masks for flush-to-file and buffer-full count. Control flow is half-buffer log draining: GuC advances `write_ptr`, samples it, sets flush flag, interrupts the host, and expects the host to copy data, update `read_ptr`, clear the flag, and acknowledge. State persists in shared log memory for event, crash dump, and state capture regions. Dependencies are Linux types and bit macros. Integration points are GuC logging interrupts, crash dump collection, state capture parsing, and log streaming files. Risks include pointer wrap mistakes, losing data when host does not acknowledge before overwrite, misusing opaque marker/version fields, and buffer-full counter truncation. Test signals include wrap/half-full simulations, interrupt-driven flush tests, crash/state-capture extraction, and overflow accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_log_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_messages_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_messages_abi.h

Purpose: defines the generic HXG message grammar shared by MMIO, CTB, SR-IOV, relay, and GuC action ABIs. Important APIs are origin/type/aux masks, request/event/fast request data/action masks, busy/retry/failure/response lengths, and success/failure payload fields. Control flow is request-response oriented: synchronous requests may receive busy, retry, failure, or success; fast requests and events do not expect normal data replies. State is transient message dwords, with action-specific payload interpretation delegated to other headers. Dependencies are bitfield macros supplied by the kernel environment. Integration points are all GuC command encoders/decoders, CTB HXG wrapping, relay messages, and error handling. Risks include origin/type confusion, masking the 12-bit request DATA0 field incorrectly, expecting replies to fast requests, and action-specific length mismatches. Test signals include encode/decode unit tests, invalid type rejection, busy/retry timeout behavior, and cross-header action message construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_messages_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_relay_actions_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_relay_actions_abi.h

Purpose: defines VF/PF relay message actions carried as opaque HXG relay payloads through GuC. Important APIs are relay ABI version constants, `GUC_RELAY_ACTION_VF2PF_HANDSHAKE`, handshake request/response fields, `GUC_RELAY_ACTION_VF2PF_QUERY_RUNTIME`, runtime response sizing/count macros, debug action range, and `GUC_RELAY_ACTION_VFXPF_TESTLOOP` opcodes. Control flow begins with ABI negotiation, then VF can query PF-owned runtime registers by index with count/remaining pagination. Debug builds can exercise no-op, busy, retry, echo, and fail behavior. State is not stored in this header, but PF/VF drivers persist negotiated version and runtime query cursor. Dependencies include `guc_relay_communication_abi.h` and HXG field macros. Integration points are SR-IOV VF capability discovery, PF register mediation, and relay selftests. Risks include production use of debug actions, oversized runtime replies, failure to handshake before later messages, and assuming version 0.0 is valid beyond negotiation wildcard. Test signals include handshake compatibility tests, paginated runtime queries, relay payload max count checks, and debug testloop coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_relay_actions_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_relay_communication_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_relay_communication_abi.h

Purpose: documents the relay transport that lets VF and PF drivers communicate through GuC. Important APIs are `GUC_RELAY_MSG_MIN_LEN`, `GUC_RELAY_MSG_MAX_LEN`, the static assertion comparing PF2GUC and VF2GUC wrapper sizes, and relay error codes modeled after errno values. Control flow is proxy based: VF sends `VF2GUC_RELAY_TO_PF`, GuC forwards `GUC2PF_RELAY_FROM_VF`, PF replies with `PF2GUC_RELAY_TO_VF`, and GuC delivers `GUC2VF_RELAY_FROM_PF`; PF can also initiate the same path. State is the relay identifier used by drivers to correlate requests and replies; payload contents remain opaque HXG messages. Dependencies are SR-IOV action and CTB/HXG headers. Integration points are VF/PF ABI negotiation, runtime register mediation, and cross-OS virtualization control. Risks include relay ID reuse, payload truncation by CTB size, wrong target VFID, and error-code translation across operating systems. Test signals include round-trip relay tests, RID correlation tests, max-size payload rejection, and relay error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_relay_communication_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_scheduler_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_scheduler_abi.h

Purpose: provides common GuC scheduler constants shared by context registration, submissions, KLV policy, and engine grouping. Important APIs are engine class IDs, maximum engine classes/instances, client priority values, GuC context id bounds, context registration flags/types, context enable/disable constants, `GUC_MAX_SCHED_GROUPS`, and `struct guc_sched_group`. Control flow is indirect: callers encode these values into GuC scheduler actions and KLVs. State persists in firmware scheduler context tables and group policies. Dependencies are Linux types and bit macros. Integration points include scheduler registration, PF/VF VGT group configuration, context policy KLVs, and engine-class mapping. Risks include class-ID drift versus firmware, exceeding 16 classes or 32 instances, interpreting unknown `GUC_ID_UNKNOWN`, and group masks that omit engines. Test signals include engine class translation tests, context registration validation, priority mapping tests, and scheduling group KLV bounds checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_scheduler_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/i915_config.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/i915_config.h

Purpose: supplies a minimal i915 compatibility API for display code compiled under Xe. The only function is `i915_fence_timeout()`, returning `MAX_SCHEDULE_TIMEOUT`. Control flow is trivial and has no side effects. State and persistence are absent. Dependencies are `linux/sched.h`. Integration points are shared i915 display code that expects the i915 configuration helper while building inside the Xe driver. Risks are semantic mismatch if a caller expects a finite timeout or module-configurable fence behavior. Test signals are compile coverage of shared display paths and any timeout-sensitive tests that should not hang indefinitely under Xe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/i915_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/i915_gtt_view_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/i915_gtt_view_types.h

Purpose: reuses i915 GTT view type definitions for Xe display paths. It includes the i915 header and defines `I915_GTT_VIEW_PARTIAL` as an unsupported sentinel intended to fail builds if partial views are used. Control flow and runtime state are absent. Dependencies are the relative i915 display header. Integration points include Xe framebuffer pinning, rotated/remapped/normal GTT view handling, and shared display plane state. Risks are accidental reliance on partial views, include-path breakage, and drift between i915 view definitions and Xe-supported mapping paths. Test signals include build coverage for normal, rotated, and remapped views, plus compile-time detection of unsupported partial-view call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/i915_gtt_view_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/i915_reg_defs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/i915_reg_defs.h

Purpose: exposes i915 register-definition types and macros to Xe display compatibility code by directly including `../../i915/i915_reg_defs.h`. There are no local functions or state. Control flow is compile-time include delegation. Dependencies are the i915 header path and whatever register abstractions it exports, especially `i915_reg_t` and offset helpers consumed by `intel_uncore.h`. Integration points are shared display register definitions and Xe wrappers that translate i915 register objects to `xe_reg`. Risks include relative include movement, ABI drift between i915 and Xe register representations, and silent propagation of i915-only assumptions. Test signals are build coverage of shared display code and read/write wrapper tests in `intel_uncore.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/i915_reg_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_clock_gating.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_clock_gating.h

Purpose: forwards shared display code to the existing i915 clock-gating header. It defines no local functions, types, or state. Control flow is compile-time include delegation. Dependencies are the relative i915 header. Integration points are display workarounds and hardware programming code that still reference i915 clock-gating declarations while building under Xe. Risks are include path drift and mismatch between i915 clock-gating declarations and Xe implementation availability. Test signals are allmodconfig/build coverage and display workaround paths that include this shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_clock_gating.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_mchbar_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_mchbar_regs.h

Purpose: forwards i915 MCHBAR register definitions into the Xe compatibility include tree. There are no local APIs beyond the include. Control flow and state are absent. Dependencies are `../../i915/intel_mchbar_regs.h`. Integration points are shared display memory/DRAM and bandwidth code that still uses i915 MCHBAR register names. Risks include relative path changes and use on platforms where Xe does not provide equivalent access plumbing. Test signals are build coverage of DRAM detection and display bandwidth initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_mchbar_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_pci_config.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_pci_config.h

Purpose: forwards i915 PCI config definitions for shared display code compiled in Xe. It contains no local state or functions. Control flow is include-only. Dependencies are the i915 PCI config header. Integration points include display probing, DRAM/bandwidth detection, and platform configuration reads that use i915 names. Risks are include-path drift and callers assuming i915 device-private structures. Test signals are compile coverage and platform probe tests that exercise PCI config reads through shared display code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_pci_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_step.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_step.h

Purpose: maps the i915 stepping type name to Xe's stepping type by including `xe_step_types.h` and defining `intel_step` as `xe_step`. Control flow and runtime state are absent. Dependencies are Xe step type definitions. Integration points are shared display and workaround code that expects an `intel_step` symbol. Risks include macro substitution surprises, missing future i915 helper APIs, and semantic drift if i915 and Xe stepping models diverge. Test signals include build coverage for stepping-dependent display workarounds and platform stepping selection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_step.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_uncore.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_uncore.h

Purpose: provides Xe-backed implementations of the i915 uncore MMIO helpers required by shared display code. Important APIs include `to_intel_uncore`, `__compat_uncore_to_mmio`, read/write helpers for 8/16/32-bit registers, `intel_uncore_read64_2x32`, posting reads, RMW, firmware/notrace variants, and unclaimed MMIO detection stub. Control flow converts an `i915_reg_t` offset into `XE_REG(...)` and dispatches to root-tile Xe MMIO accessors. State is the embedded `xe_device.uncore` and root tile MMIO mapping; no extra persistence is added. Dependencies include `i915_reg_defs.h`, `xe_device.h`, `xe_device_types.h`, and `xe_mmio.h`. Integration points are shared display register access, early display init, and power/interrupt paths. Risks include root-tile-only access for registers that may need media/tile routing, weak unclaimed-MMIO detection, and 64-bit read retry assumptions. Test signals include display MMIO read/write tests, register tracing expectations, and 64-bit timestamp counter consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_uncore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_uncore_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_uncore_trace.h

Purpose: stubs the i915 register tracepoint macro for Xe compatibility. `trace_i915_reg_rw(a...)` expands to an empty `do { } while (0)`. There is no runtime control flow or state. Dependencies are none. Integration points are shared display code that emits i915 MMIO trace events when built in i915 but must compile under Xe. Risks are loss of register trace observability and tests that assume trace events exist. Test signals are build coverage and manual tracing expectations around display MMIO debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/intel_uncore_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/vlv_iosf_sb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/vlv_iosf_sb.h

Purpose: supplies stubbed Valleyview IOSF sideband interfaces for Xe builds. Important APIs are `enum vlv_iosf_sb_unit`, `vlv_iosf_sb_get`, `vlv_iosf_sb_read`, `vlv_iosf_sb_write`, and `vlv_iosf_sb_put`; the functions are no-ops or return zero. Control flow and state are intentionally absent. Dependencies include Linux types and `vlv_iosf_sb_reg.h`. Integration points are shared display code that conditionally references VLV IOSF paths but is not expected to need real IOSF access under Xe. Risks are silent success on accidental runtime use and zero-valued reads masking bugs. Test signals should include platform guards proving VLV-only paths do not execute in Xe, plus build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/vlv_iosf_sb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/vlv_iosf_sb_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/vlv_iosf_sb_reg.h

Purpose: forwards Valleyview IOSF sideband register definitions from the i915 tree. It defines no local state or behavior. Control flow is compile-time include delegation. Dependencies are `../../i915/vlv_iosf_sb_reg.h`. Integration points are shared display code compiled under Xe that still includes VLV register names. Risks are accidental use together with the no-op IOSF accessors, and include-path drift. Test signals are build coverage and platform feature guards preventing runtime use on Xe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/vlv_iosf_sb_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/intel_fbdev_fb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/intel_fbdev_fb.c

Purpose: adapts fbdev framebuffer allocation and mapping to Xe BOs. Important APIs are `intel_fbdev_fb_pitch_align`, `intel_fbdev_fb_prefer_stolen`, `intel_fbdev_fb_bo_create`, `intel_fbdev_fb_bo_destroy`, and `intel_fbdev_fb_fill_info`. Control flow aligns fbdev stride to `XE_PAGE_SIZE`, prefers stolen memory only when present, not DGFX, not affected by display workaround 22019338487, and large enough, then falls back to VRAM/system-compatible GGTT BO creation. State is pinned/mapped BO lifetime and `fb_info.fix`/screen mapping metadata. Dependencies include Xe BO, stolen manager, TTM, and workaround headers. Integration points are DRM fbdev emulation and initial console scanout. Risks include the FIXME around page-size stride alignment, stolen-memory overuse, incorrect physical address reporting for system BOs, and pin-count underflow regressions. Test signals include fbdev creation on integrated and DGFX devices, stolen fallback, smem fields, and atomic cleanup pin accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/intel_fbdev_fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display.c

Purpose: is the central Xe-to-Intel-display bridge. Important APIs include display probe/defer/hook setup, early/full init and fini actions, register/unregister, IRQ handling/reset/postinstall, system suspend/shutdown/resume, runtime PM suspend/resume, and the `intel_display_parent_interface`. Control flow gates everything on `xe->info.probe_display`, initializes opregion/DRAM/bandwidth/noirq/nogem/GEM display stages, uses devm/drmm cleanup actions, routes display and GSE interrupts, and orders PM around power domains, clients, HPD, DMC, opregion, encoders, and D3cold. State persists in `xe->display`, DRM driver feature bits, runtime display device state, pending commit cleanup, and power-domain state. Dependencies are broad shared Intel display subsystems plus Xe BO/DSB/frontbuffer/HDCP/panic/pcode/RPM/stolen interfaces. Integration points are PCI probe, DRM driver features, interrupt dispatch, runtime PM, and display device parent callbacks. Risks are PM ordering regressions, incomplete cleanup before D3cold, stale `probe_display` feature bits, and root-tile assumptions in callbacks. Test signals include display probe/no-display fallback, suspend/resume and runtime D3cold tests, hotplug/IRQ tests, and devm cleanup error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display.h

Purpose: declares the Xe display lifecycle, IRQ, and PM entry points, with no-op inline stubs when `CONFIG_DRM_XE_DISPLAY` is disabled. Important APIs are `xe_display_driver_probe_defer`, `xe_display_driver_set_hooks`, `xe_display_probe`, `xe_display_init_early`, `xe_display_init`, register/unregister, IRQ functions, and suspend/resume/runtime PM hooks. Control flow is compile-time conditional: real functions are linked only with display support; otherwise callers get harmless zero/no-op behavior. State is not owned by this header but all functions operate on `struct xe_device`. Dependencies are `xe_device.h` and forward declaration of `drm_driver`. Integration points are the Xe driver probe/remove, IRQ, and PM call graph. Risks include prototype drift versus `xe_display.c`, hidden no-op behavior masking missing display support, and the stub declaring `xe_display_driver_remove` without a matching real prototype. Test signals are build coverage with display enabled and disabled, plus probe paths verifying driver feature bits are set only when display is built and requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_bo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_bo.c

Purpose: implements the display BO parent interface for Xe GEM/TTM objects. Important APIs are interface callbacks for protection checks, PXP key check, mmap, page reads, framebuffer init/fini, and framebuffer lookup. Control flow validates 64 KiB physical alignment for modifiers that need it, takes a BO reference, reserves the TTM BO, forces WC caching when safe, rejects VM-bound BOs whose caching cannot change, unpins pinned kernel framebuffers during fini, and rejects DGFX framebuffer lookup unless the BO can migrate to VRAM or is an imported sg BO. State is BO flags, pin/ref counts, TTM reservation, and framebuffer ownership. Dependencies include DRM GEM, Intel FB helpers, Xe BO, and PXP. Integration points are framebuffer creation, scanout validation, protected content, and display mmap. Risks include caching flag changes after VM bind, missing `XE_BO_FLAG_NEEDS_64K`, DGFX placement errors, and unbalanced BO references on error. Test signals include framebuffer init/fini refcount tests, modifier alignment validation, VM-bound rejection, imported dma-buf scanout, and PXP protected object paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_bo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_bo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_bo.h

Purpose: exports `xe_display_bo_interface` to the display parent interface. It contains no control flow or state beyond the extern declaration. Dependencies are the interface type declaration from display parent code at use sites. Integration points are `xe_display.c` parent interface initialization and framebuffer/display BO operations. Risks are limited to symbol/prototype drift if the implementation changes. Test signals are build/link coverage and display framebuffer creation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_bo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_pcode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_pcode.c

Purpose: adapts display pcode operations to Xe pcode helpers. Important APIs are interface callbacks `read`, `write`, and `request`, implemented by `xe_display_pcode_read`, `xe_display_pcode_write_timeout`, and `xe_display_pcode_request`. Control flow converts `drm_device` to `xe_device`, selects the root tile, and forwards mailbox operations to `xe_pcode_*`. State is external pcode mailbox state and root tile selection; this file stores nothing. Dependencies are `xe_device.h`, `xe_pcode.h`, and the display parent interface. Integration points are shared display code requiring pcode mailbox reads/writes for power, display, or platform programming. Risks include root-tile assumption on multi-tile platforms and timeout propagation. Test signals include pcode mailbox success/failure tests, timeout behavior, and display features that require pcode requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_pcode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_pcode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_pcode.h

Purpose: declares `xe_display_pcode_interface` for registration in the display parent interface. There is no local control flow or state. Integration points are `xe_display.c` and shared display pcode users. Risks are symbol drift only. Test signals are build/link coverage and pcode-using display paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_pcode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_rpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_rpm.c

Purpose: implements the display runtime power-management interface on top of Xe PM helpers. Important callbacks are get, get_raw, get_if_in_use, get_noresume, put, put_raw, put_unchecked, suspended, and placeholder assert functions. Control flow maps display wakeref operations to `xe_pm_runtime_*`; successful gets return `ERR_PTR(-ENOENT)` as a sentinel meaning a reference exists but no ref-tracker object is supplied. State is Xe runtime PM reference count and device suspend state. Dependencies include display core/RPM headers, Xe device types, and Xe PM. Integration points are all shared display code that brackets MMIO or power-domain operations with runtime wakerefs. Risks include the nonstandard wakeref sentinel, put only acting when wakeref is non-NULL, and unimplemented assertions hiding runtime PM misuse. Test signals include runtime suspend/resume refcount tests, get-if-in-use behavior, noresume paths, and future assertion enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_rpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_rpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_rpm.h

Purpose: exports `xe_display_rpm_interface`. It has no runtime behavior or owned state. Integration points are the parent display interface and shared display runtime PM helpers. Risks are declaration/implementation drift. Test signals are build/link coverage and runtime PM path tests through `xe_display_rpm.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_rpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_vma.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_vma.h

Purpose: defines the Xe-backed compatibility `struct i915_vma` used by shared display framebuffer pinning code. Important fields are `ref`, `bo`, optional `dpt`, and GGTT `node`. Control flow is external in `xe_fb_pin.c`, which refcounts, pins, maps, and frees these objects. State persists while a framebuffer or plane state holds a scanout mapping. Dependencies are `linux/refcount.h` plus forward declarations for Xe BO and GGTT node. Integration points are `intel_fb_pin_to_ggtt`, plane pin/unpin, fbdev VMA reuse, DPT mappings, and initial plane setup. Risks include the compatibility name hiding that this is not a full i915 VMA, refcount imbalance, and callers expecting fields absent here. Test signals include plane state reuse, fbdev VMA sharing, DPT cleanup, and unpin lifetime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_vma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_wa.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_wa.c

Purpose: exposes display workaround query `intel_display_needs_wa_16023588340` for shared display code. Control flow converts `intel_display` to `xe_device`, selects the root MMIO GT, and checks the Xe GT workaround table for WA 16023588340. State is the generated/out-of-band workaround metadata, not local storage. Dependencies include Intel display workaround headers, Xe device and WA helpers, and generated `xe_wa_oob.h`. Integration points are display workaround programming paths. Risks include null root MMIO GT handling, generated WA table drift, and platform gating errors. Test signals include workaround table build generation and platform-specific display workaround checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_wa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_dsb_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_dsb_buffer.c

Purpose: implements display DSB buffer management using Xe BOs. Important callbacks are GGTT offset lookup, dword write/read, fill, create, cleanup, and flush_map. Control flow allocates an `intel_dsb_buffer`, creates a pinned/mapped GGTT BO in VRAM for DGFX or suitable memory otherwise, writes via `iosys_map`, and flushes with a write memory barrier plus L2 flush before display/MMIO use. State is the DSB command BO, buffer size, and mapped command memory. Dependencies include Xe BO/device types and display parent interface. Integration points are Intel display DSB command generation and MMIO programming acceleration. Risks include size/page alignment mismatch, bounds warnings in fill, stale cache data without flush, and allocation placement failures. Test signals include DSB allocation/free tests, command write/read/fill verification, GGTT address validity, and coherency tests on discrete GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_dsb_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_dsb_buffer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_dsb_buffer.h

Purpose: declares `xe_display_dsb_interface`. No local state or control flow exists. Integration points are `xe_display.c` parent interface setup and display DSB users. Risks are limited to symbol drift. Test signals are build/link coverage and DSB command-buffer paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_dsb_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_fb_pin.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_fb_pin.c

Purpose: implements Xe framebuffer pinning for shared Intel display plane code. Important APIs are `intel_fb_pin_to_ggtt`, `intel_fb_unpin_vma`, `intel_plane_pin_fb`, `intel_plane_unpin_fb`, and `intel_fb_get_map`, plus internal DPT/GGTT mapping writers for normal, remapped, and rotated views. Control flow validates visible VRAM for clear-color access, reserves/migrates/validates and pins BOs, builds DPT page tables or GGTT transform nodes, flushes L2, reuses old/fbdev VMAs when possible, refcounts VMAs, and removes DPT/GGTT mappings on final unpin. State includes BO pin count, TTM placement, DPT BOs, GGTT nodes, plane `surf`, and VMA refcounts. Dependencies include Intel FB view helpers, Xe BO/GGTT/PM/validation/VRAM helpers, and `xe_display_vma.h`. Integration points are atomic plane updates, fbdev scanout, initial plane setup, rotated/remapped scanout, and GGTT address programming. Risks include DPT size math, rotated/remapped tile ordering, 64 KiB VRAM alignment, cleanup on partial failure, pin-count imbalance, and root-tile-only mapping. Test signals include normal/rotated/remapped plane pin tests, fbdev VMA reuse, DGFX small-BAR rejection, migration/validation error injection, and unpin leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_fb_pin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_frontbuffer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_frontbuffer.c

Purpose: implements a minimal Xe frontbuffer wrapper for shared display code. Important callbacks are get, ref, put, and flush_for_display. Control flow allocates `struct xe_frontbuffer`, initializes the embedded `intel_frontbuffer`, takes a GEM object reference, increments/decrements a `kref`, and frees the wrapper plus GEM reference on final put. `flush_for_display` is currently empty. State is the wrapper refcount and held GEM object reference. Dependencies are DRM GEM and Intel frontbuffer helpers. Integration points are the display parent interface and frontbuffer tracking in shared display code. Risks include missing flush behavior if cache coherency expectations change, allocation failure returning NULL, and mismatched frontbuffer/GEM lifetime. Test signals include frontbuffer allocation/ref/put lifetime tests and display coherency tests that would expose missing flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_frontbuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_frontbuffer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_frontbuffer.h

Purpose: declares `xe_display_frontbuffer_interface`. It owns no state and has no control flow. Integration points are `xe_display.c` parent interface setup and shared frontbuffer tracking code. Risks are symbol drift and missing include type visibility at use sites. Test signals are build/link coverage and frontbuffer lifetime tests in `xe_frontbuffer.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_frontbuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_hdcp_gsc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_hdcp_gsc.c

Purpose: implements HDCP 2.x GSC messaging for the display parent interface. Important callbacks are GSC status check, context allocation/free, and synchronous message send. Control flow verifies media GT and GSC firmware availability, takes runtime PM and forcewake, checks proxy init, allocates a two-page GGTT BO for input/output, emits GSC headers with an HDCP HECI address, submits packets through `xe_gsc_pkt_submit_kernel`, retries up to 20 times on pending with 50 ms sleeps, validates output headers, and copies the reply. State is `intel_hdcp_gsc_context` containing Xe device, command BO, and GGTT input/output addresses. Dependencies include GSC command header ABI, Xe GSC proxy/submit/map/PM/forcewake/firmware helpers, and i915 HDCP interface types. Integration points are HDCP authentication and protected content display. Risks include PAGE_SIZE message limits, pending retry exhaustion, media GT absence, forcewake failure, stale command buffer contents, and incorrect output offsets. Test signals include HDCP GSC status gating, oversized message rejection, pending retry behavior, packet-submit failure injection, and context free leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_hdcp_gsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_hdcp_gsc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_hdcp_gsc.h

Purpose: declares `xe_display_hdcp_interface`. There is no local state or control flow. Integration points are `xe_display.c` parent interface setup and shared Intel HDCP code. Risks are symbol drift only. Test signals are build/link coverage and HDCP GSC paths in `xe_hdcp_gsc.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_hdcp_gsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_initial_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_initial_plane.c

Purpose: handles inherited boot/firmware initial plane scanout for Xe display. Important callbacks are vblank wait, initial object allocation, setup, and config_fini. Control flow polls `PIPE_FRMTMSTMP` because early Xe lacks IRQ, derives a BO from initial plane base/size, validates DGFX GGTT PTE DM bit and visible VRAM range, uses stolen memory on integrated platforms when suitable, initializes the Intel framebuffer around the BO, and pins it to GGTT for plane state. State is the created pinned/mapped BO, framebuffer ownership, `plane_config->vma`, and plane `surf`. Dependencies include Xe GTT defs, MMIO, GGTT, BO, VRAM, fbdev stolen preference, and Intel initial plane helpers. Integration points are boot splash takeover, fbdev console, and early modeset. Risks include invalid initial plane PTEs, stolen memory overcommit, page-size rounding errors, early vblank timeout, and empty `config_fini`. Test signals include BIOS/firmware framebuffer takeover on DGFX and integrated devices, invalid PTE rejection, stolen-size discard, and early vblank wait behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_initial_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_initial_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_initial_plane.h

Purpose: exports `xe_display_initial_plane_interface`. It contains no runtime behavior or owned state. Integration points are `xe_display.c` and shared initial-plane takeover code. Risks are declaration drift. Test signals are build/link coverage and initial plane paths in `xe_initial_plane.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_initial_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_panic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_panic.c

Purpose: supports DRM panic rendering into Xe scanout buffers. Important APIs are the panic interface callbacks allocate, setup, and finish, plus `xe_panic_page_set_pixel`. Control flow allocates an `intel_panic` context, rejects non-visible VRAM, installs a pixel writer, computes linear or tiling-derived offsets, maps the needed page using visible VRAM addresses or `ttm_bo_kmap_try_from_panic`, reuses the current page mapping when possible, writes pixels through `iosys_map`, and unmaps/flushes CPU mappings at finish. State is a resource cursor, temporary page map, and current page index. Dependencies include DRM panic/cache helpers, Intel framebuffer tiling, Xe BO, and resource cursor utilities. Integration points are emergency panic screen drawing. Risks include panic-context allocation failure, invisible VRAM, mapping failure, page cursor errors when moving backward, and cache flushing for system memory. Test signals include panic path smoke tests, visible/nonvisible VRAM cases, tiled offset validation, and page transition/unmap checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_panic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_panic.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_panic.h

Purpose: declares `xe_display_panic_interface` for the display parent interface. No local state or control flow exists. Integration points are `xe_display.c` and DRM panic support. Risks are symbol drift. Test signals are build/link coverage and panic rendering paths in `xe_panic.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_panic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_stolen.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_stolen.c

Purpose: implements display stolen-memory node operations on top of Xe BOs. Important callbacks allocate/free nodes, insert/remove pinned stolen BOs in range, query initialization/allocation, and report node offset/address/size. Control flow allocates `intel_stolen_node`, creates pinned stolen BOs with range and alignment adjustments, forbids start below 4 KiB, removes nodes by unpinning/unmapping, and computes GPU addresses using the stolen GPU offset plus resource cursor offset. State is the node's `xe_device` pointer and optional stolen BO. Dependencies include Xe stolen TTM manager, resource cursor, validation types, and display parent interface. Integration points are shared display allocation of stolen regions for framebuffers or display features. Risks include range alignment changing requested placement, BO allocation failures, address calculation if resource layout changes, and null BO misuse. Test signals include stolen manager presence checks, insert/remove range tests, alignment/start-boundary tests, and address/size query validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_stolen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_stolen.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_stolen.h

Purpose: declares `xe_display_stolen_interface`. It owns no state and has no control flow. Integration points are `xe_display.c` and shared display stolen-memory users. Risks are declaration drift only. Test signals are build/link coverage and stolen allocation tests in `xe_stolen.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_stolen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_tdf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_tdf.c

Purpose: provides the display transient data flush hook for Xe. The only API is `intel_td_flush`, which converts `intel_display` to `xe_device` and calls `xe_device_td_flush`. Control flow and state are minimal; persistence is external hardware/cache state. Dependencies are Intel display core/TDF declarations and `xe_device.h`. Integration points are shared display TDF paths on platforms requiring transient flushes. Risks are root-device conversion assumptions and no local error reporting. Test signals include platform paths that trigger TDF flush and MMIO/cache coherency tests around display updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_tdf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_alu_commands.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_alu_commands.h

Purpose: defines command streamer ALU opcodes, operands, and instruction encoding helpers. Important APIs are `CS_ALU_OPCODE_*`, `CS_ALU_OPERAND_*`, `CS_ALU_INSTR`, `__CS_ALU_INSTR`, and convenience macros such as `CS_ALU_INSTR_LOAD`, `ADD`, `STORE`, and `STOREINV`. Control flow is compile-time packet construction; runtime consumers emit these dwords into command buffers. State is the command stream and ALU register/flag state in hardware, not local memory. Dependencies are `xe_instr_defs.h` for bitfield helpers. Integration points include MI_MATH sequences, register programming batches, and GPU command emitters. Risks include operand width mistakes, invalid register indices, macro concatenation misuse, and architecture opcode drift. Test signals include command dword golden tests, MI_MATH execution tests, and assembler/emitter validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_alu_commands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_gfx_state_commands.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_gfx_state_commands.h

Purpose: defines basic graphics state command encoding. Important APIs are `GFX_STATE_OPCODE`, `GFX_STATE_CMD`, and `STATE_WRITE_INLINE`. Control flow is compile-time construction of a state-command header using `XE_INSTR_GFX_STATE`. State is the GPU command stream generated by callers. Dependencies are `xe_instr_defs.h`. Integration points are batch builders that emit inline graphics state writes. Risks are opcode field drift and using the macro on platforms with different state command formats. Test signals include golden command dword tests and GPU batch execution that uses `STATE_WRITE_INLINE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_gfx_state_commands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_gfxpipe_commands.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_gfxpipe_commands.h

Purpose: defines graphics pipeline command header encodings and many 3D/compute/common command IDs. Important APIs are pipeline/opcode/subopcode masks, `GFXPIPE_*_CMD` constructors, `GFXPIPE_MATCH_MASK`, and command constants such as `STATE_BASE_ADDRESS`, `PIPELINE_SELECT`, shader/state pointer commands, mesh/task commands, and binding/table/sample commands. Control flow is compile-time dword generation for command buffers. State is hardware graphics pipeline state programmed by emitted packets. Dependencies are `xe_instr_defs.h`. Integration points include render/compute batch emitters, parser tables, and workarounds that match command headers. Risks include command ID drift across graphics generations, confusing common/single/3D/compute pipelines, and incomplete length/data fields. Test signals include command parser golden tests, batch emit validation, and generation-specific command availability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_gfxpipe_commands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_gpu_commands.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_gpu_commands.h

Purpose: defines BLT, memory copy/set, fast copy/color fill, control-surface copy, and pipe-control command constants. Important APIs include `XY_CTRL_SURF_COPY_BLT`, CCS and MOCS masks, `XY_FAST_COLOR_BLT_CMD`, `XY_FAST_COPY_BLT_CMD`, `MEM_COPY_CMD`, `PVC_MEM_SET_CMD`, `GFX_OP_PIPE_CONTROL`, and many pipe-control flush/invalidate bits. Control flow is compile-time packet construction by emitters. State is GPU memory/cache/CCS state affected by emitted commands. Dependencies are register bit macros from `xe_reg_defs.h`. Integration points are migration, blit, clear/copy, cache flush, TLB invalidate, and synchronization paths. Risks include generation-specific MOCS/CCS field differences, wrong pipe-control bit combinations, and cache coherency regressions. Test signals include blit/copy functional tests, CCS metadata tests, cache/TLB invalidation tests, and golden command dwords by platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_gpu_commands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_gsc_commands.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_gsc_commands.h

Purpose: defines GSCCS-specific command headers. Important APIs are `GSC_OPCODE`, `GSC_CMD_DATA_AND_LEN`, `__GSC_INSTR`, `GSC_HECI_CMD_PKT`, `GSC_FW_LOAD`, and `GSC_FW_LOAD_LIMIT_VALID`. Control flow is compile-time encoding of fixed-length GSC commands; comments explain that data and length bits are treated as one field because current commands do not use separate data. State is GSC command streamer execution state. Dependencies are `xe_instr_defs.h`. Integration points include GSC firmware loading and HECI packet submission, including HDCP/PXP related flows. Risks include future commands needing distinct data and length fields, incorrect fixed lengths, and opcode drift. Test signals include GSC firmware load tests, HECI packet submission tests, and command dword golden checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_gsc_commands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_instr_defs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_instr_defs.h

Purpose: provides common GPU instruction header fields and length helpers. Important APIs are `XE_INSTR_CMD_TYPE`, instruction type values for MI/GSC/video/gfxpipe/gfx_state, `XE_INSTR_LEN_MASK`, and `XE_INSTR_NUM_DW`. Control flow is compile-time packet header construction used by all instruction family headers. State is command-buffer dwords emitted by callers. Dependencies are `xe_reg_defs.h` for GENMASK and REG_FIELD_PREP. Integration points are all Xe GPU command emission headers. Risks include the fact that not all commands use the common 7:0 length field, shared value for video and gfxpipe type, and off-by-two length encoding mistakes. Test signals include command dword golden tests and static checks for command length emitters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_instr_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_mfx_commands.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_mfx_commands.h

Purpose: defines media fixed-function command encodings. Important APIs are MFX subtype/opcode/subopcode/flags masks, `XE_MFX_INSTR`, `MFX_WAIT`, sync-control bits, and `CRYPTO_KEY_EXCHANGE`. Control flow is compile-time command header construction for video/media command buffers. State is media pipeline synchronization and crypto command state in hardware. Dependencies are `xe_instr_defs.h`. Integration points include media engines, PXP/crypto key exchange, and MFX wait synchronization. Risks include opcode/subtype drift and misuse of sync-control flags. Test signals include media command golden dwords, PXP key exchange flows, and media wait/synchronization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_mfx_commands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_mi_commands.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_mi_commands.h

Purpose: defines MI command encodings used by all GT engines. Important APIs include `MI_NOOP`, interrupts, arbitration, batch start/end, `MI_MATH`, semaphore wait, store/load register and memory commands, flush/invalidate bits, copy memory, appid/session macros, and XeLP semaphore token fields. Control flow is compile-time generation of command-buffer dwords; hardware executes these for synchronization, register access, memory writes, and batch control. State is command streamer, registers, memory, and cache/TLB state affected by emitted commands. Dependencies are `xe_instr_defs.h` and ALU command consumers for MI_MATH payloads. Integration points include ring setup, scheduler batches, GPU synchronization, register save/restore, and debug commands. Risks include length-field off-by-one errors, GGTT versus PPGTT address flag misuse, semaphore compare mistakes, and generation-specific token support. Test signals include batch execution tests, semaphore timeout paths, register load/store tests, and golden command encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/instructions/xe_mi_commands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_bars.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_bars.h

Purpose: defines PCI BAR indices used by Xe. Important APIs are `GTTMMADR_BAR` for MMIO/GTT, `LMEM_BAR` for VRAM, and `VF_LMEM_BAR` for VF VRAM. Control flow and state are absent; callers use these constants during PCI resource discovery and mapping. Dependencies are none. Integration points are device probe, MMIO mapping, local-memory BAR handling, and SR-IOV VF resource setup. Risks include platform-specific BAR layout changes and confusing PF/VF local-memory BARs. Test signals include PCI probe on PF and VF devices, BAR resource validation, and VRAM aperture mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_bars.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_engine_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_engine_regs.h

Purpose: defines per-engine MMIO base addresses and register/bitfield macros for render, copy, compute, video, video enhance, and GSC command streamer engines. Important APIs include ring base constants, `ENGINE_ID`, ring head/tail/start/control, PSMI/power context, ACTHD/IPEHR/INSTDONE, interrupts, MI mode, command CCTL/MOCS fields, chicken/debug registers, context control, nonprivileged register slots, execlist status/control, timestamps, GPRs, and VDBOX clock-gating registers. Control flow is external hardware programming: engine setup/reset/scheduler/debug code reads and writes these addresses. State is all engine-local hardware state, context control, interrupts, and debug counters. Dependencies are `xe_reg_defs.h` and page size constants. Integration points include engine discovery, ring management, GuC scheduling, workarounds, force-to-nonpriv programming, and hang/error capture. Risks include wrong base for engine instance, masked register write semantics, MOCS index/value confusion, nonpriv slot range mistakes, and generation-specific register validity. Test signals include engine init/reset tests, register readback on each class, workaround programming validation, hang capture, and nonpriv access tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_engine_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_eu_stall_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_eu_stall_regs.h

Purpose: defines Xe HPC EU stall sampling MMIO registers. Important APIs are `XEHPC_EUSTALL_BASE`, base address/buffer size/enable fields, upper base, report and report1 read/write pointer and overflow bits, and `XEHPC_EUSTALL_CTRL` MOCS/sample-rate fields. Control flow is external: performance code programs buffer address and rate, enables sampling, and reads pointer/overflow state. State is hardware sampling buffer configuration and producer/consumer pointers. Dependencies are MCR register definitions from `xe_reg_defs.h`. Integration points include perf/telemetry and EU stall analysis. Risks include MCR steering mistakes, buffer size encoding errors, overflow/drop handling, and MOCS mismatch. Test signals include perf sampling enable/disable tests, pointer wrap tests, overflow accounting, and MCR read/write coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_eu_stall_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_gsc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_gsc_regs.h

Purpose: defines GSC HECI and firmware-status registers. Important APIs include platform HECI base addresses, `HECI_H_CSR` bits for interrupt/status/ready/reset, `HECI_FWSTS1..6`, HECI1 current/proxy/init/HuC auth fields, `HECI_H_GS1_ER_PREP`, and `GSCI_TIMER_STATUS` values. Control flow is external GSC firmware/proxy code polling readiness, reset, proxy normal state, HuC auth, and timer reset status. State is hardware/firmware status registers. Dependencies are Xe register definitions and Linux types. Integration points include GSC firmware load, proxy initialization, HDCP/PXP messaging, error recovery, and media GT forcewake. Risks include platform base selection mistakes, HECI1 versus HECI2 firmware-status semantics, polling timeout errors, and reset-state races. Test signals include GSC probe on supported platforms, proxy init checks, firmware status polling, reset/error recovery, and HDCP status gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_gsc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_gt_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_gt_regs.h

Purpose: is a large GT-level register map for graphics/media hardware. Important APIs include media GT GSI offset/length, workpoint/frequency registers, forcewake ack/domain registers, GMD ID fields, MCR selectors, MOCS/LNCF MOCS fields, compression and flat CCS registers, aux invalidation, many chicken/workaround registers, fuse/topology registers, reset and clock/power gating registers, RPS/RC6/perf limit registers, L3/SQ/LSC/EU controls, CCS mode, GT status, and SFC done registers. Control flow is external: probe, topology discovery, forcewake, power management, cache/CCS setup, workarounds, and perf code program/read these macros. State is persistent hardware register state across GT init, reset, suspend/resume, and workload execution. Dependencies are `xe_reg_defs.h` and MCR/masked register semantics. Integration points span GT init, memory/cache policy, media/render power, topology/fuse detection, workarounds, TDF, and performance telemetry. Risks include generation-specific register validity, MCR steering errors, masked-write semantics, forcewake domain mistakes, fuse bit interpretation drift, and media GT offset translation. Test signals include platform bring-up register readback, GT reset/suspend resume, topology detection tests, workaround verification, forcewake tests, and perf/power telemetry validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_gt_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_gtt_defs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_gtt_defs.h

Purpose: defines GGTT/PPGTT PTE/PDE bitfields used by Xe memory management and display scanout. Important APIs include PAT bits for GGTT/PPGTT, address mask, GGTT VFID field, GuC GGTT top, page-size bits for 2M/1G/64K, device-memory bits, access-enable/null/present/RW bits, and USM AE. Control flow is compile-time PTE construction and hardware page-table programming by memory managers and GGTT helpers. State is GPU page table entries and address translation behavior. Dependencies are kernel bit macros. Integration points include GGTT encoding, PPGTT page-table setup, SR-IOV VF GGTT tagging, display DPT/PTE creation, and GuC memory placement. Risks include overlapping bit definitions between GGTT and PPGTT contexts, wrong address mask alignment, VFID encoding errors, and PAT/generation differences. Test signals include page-table encoding golden tests, GGTT display mapping tests, 64K/2M/1G mapping tests, and SR-IOV VF address translation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_gtt_defs.h -->
