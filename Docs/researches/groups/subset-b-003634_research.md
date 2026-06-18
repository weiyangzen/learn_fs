# Research: subset-b-003634 Imagination Rogue firmware interface headers

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_cr_defs_client.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_cr_defs_client.h

Purpose: This generated-style register definition header exposes client-visible Rogue control register offsets and bitfield helpers for tiling, screen sizing, anti-aliasing, and macrotile geometry. It is narrow by design: no code paths, no storage, and no functions, only constants that user/kernel command builders use when programming fields later embedded in FWIF command and HWRT data structures.

Important APIs/types/functions: The main exported constants are `ROGUE_CR_TE_AA` and its `Y2`, `Y`, `X`, and `X2` enable/shift/clear masks; `ROGUE_CR_TE_MTILE1` and `ROGUE_CR_TE_MTILE2` X/Y macrotile boundary fields; `ROGUE_CR_TE_SCREEN` tile-space maximum X/Y fields; `ROGUE_CR_PPP_SCREEN` pixel-space maximum X/Y fields; and `ROGUE_CR_ISP_MTILE_SIZE` macrotile dimensions. There are no C types or callable APIs.

Control flow: None. Consumers compose register words by shifting values into these field definitions and masking with the `CLRMSK`/`MASKFULL` constants.

State and persistence behavior: The header itself has no state. Its constants define hardware-visible state that persists only when written to GPU registers or copied into FW-shared structures such as `rogue_fwif_hwrtdata_common`.

Dependencies and integration points: It is independent except for Linux integer macro conventions. It integrates with render target setup, tiler/macrotiler configuration, MSAA setup, and ISP region sizing. The matching kernel driver must keep these constants aligned with the hardware TRM and firmware expectations.

Risks: Incorrect masks or shifts corrupt register programming and can produce bad tiling, wrong screen bounds, MSAA artifacts, or GPU faults. Because this file is client-visible, ABI mismatches can affect userspace command generation. It has no compile-time layout checks.

Test signals: Build coverage catches syntax only. Functional signals are render tests across no-MSAA/2x/4x paths, large and odd framebuffer sizes, macrotile boundary cases, and comparison of generated register words against known-good traces or hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_cr_defs_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_defs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_defs.h

Purpose: This header provides common Rogue GPU constants used across firmware boot, reset, MMU, power, cache, and feature setup code. It sits below the FWIF structures and above raw register definitions by combining `pvr_rogue_cr_defs.h` fields into reusable policy macros.

Important APIs/types/functions: The file exports OS/thread limits (`ROGUE_FW_MAX_NUM_OS`, `ROGUE_FW_HOST_OS`, `ROGUE_FW_THREAD_0/1`), cache-line conversion (`GET_ROGUE_CACHE_LINE_SIZE`), maximum geometry/fragment contexts, all-on/all-auto clock-control values, S7 soft-reset group masks, PM physical/virtual page sizes, dust/phantom/Bernado/BlackPearl cluster-count rounding macros, FW MMU context IDs, CAT base address macros (`BIF_CAT_BASEX`, `FWCORE_MEM_CAT_BASEX`), remap field aliases, shared register capacity constants, timer tick size, no-HW multicore cap, SLC cache thresholds, FW boot-stage register, virtualization register stride, HWPerf feature marker, and TRP core cap. There are no structs or functions.

Control flow: None directly. The reset masks imply a hardware reset sequence: dusts, Jones blocks, optional BIF/SLC/Garten, then secondary blackpearl/pixel/CDM/vertex reset domains. Consumers choose masks based on feature and power state.

State and persistence behavior: No local state. Constants determine persistent hardware register values, firmware-visible initialization choices, MMU context mappings, and virtualized OS partition geometry.

Dependencies and integration points: Depends on `pvr_rogue_cr_defs.h` for raw register fields and Linux `BIT`. It is included by `pvr_rogue_fwif.h` and by lower-level driver code configuring clocking, reset, FW boot, PM memory, and virtualization.

Risks: This is a high-impact constants file. Wrong reset masks can leave functional blocks live during reset or over-reset shared units. Wrong page sizes or CAT base formulas can break PM allocation and MMU setup. `GET_ROGUE_CACHE_LINE_SIZE` depends on signed positive input semantics and should not be used with unknown-width values without validation.

Test signals: Kernel build, boot-to-firmware-init tests, GPU reset/HWR recovery loops, PM freelist allocation tests, virtualization OSID tests, and hardware trace comparisons for clock/reset register writes are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif.h

Purpose: This is the central host/kernel/firmware interface contract for Rogue GPUs. It defines shared firmware control blocks, queue command packets, context objects, HWR records, boot/init payloads, timer correlation data, GPU utilization accounting, freelists, render-target state, sync checkpoint values, command magic, and many command opcodes. Most structs are firmware ABI, not normal in-kernel private data.

Important APIs/types/functions: Logging exports `ROGUE_FWIF_LOG_TYPE_*`, `ROGUE_FWIF_LOG_GROUPS_STRING_LIST`, and `rogue_fwif_log_group_map_entry`. Trace/debug state is held in `rogue_fwif_tracebuf`, `rogue_fwif_tracebuf_space`, `rogue_fwif_file_info_buf`, and `rogue_fw_fault_info`. System and per-OS state use `rogue_fwif_sysdata`, `rogue_fwif_osdata`, `rogue_fwif_os_runtime_flags`, and connection enums. HWR data is modeled through `rogue_hwrtype`, `rogue_bifinfo`, `rogue_mmuinfo`, `rogue_pollinfo`, `rogue_tlbinfo`, `rogue_eccinfo`, `rogue_hwrinfo`, and `rogue_fwif_hwrinfobuf`. Initialization/configuration includes `rogue_fwif_fwmemcontext`, context state structs, `rogue_fwif_fwcommoncontext`, render/compute/TDM/transfer context wrappers, `rogue_fwif_runtime_cfg`, `rogue_fwif_osinit`, `rogue_fwif_sysinit`, `rogue_fwif_compchecks`, `rogue_hwperf_bvnc`, PDVFS OPP structs, and register-config records. Queues are defined by `rogue_fwif_ccb_ctl`, `rogue_fwif_kccb_cmd`, `rogue_fwif_fwccb_cmd`, `rogue_fwif_ccb_cmd_header`, and work-estimation packets. KCCB commands include kick, MMU cache invalidation, breakpoint, SLC flush/invalidate, cleanup, power, Z/S backing, freelist growth/reconstruction, write-offset update, health check, force update, combined geom/frag kick, OS online state, register config, HWPerf config/control, clock speed changes, log type update, PDVFS limits, priority change, PHR/watchdog/counter dump, and custom counter selection. FWCCB commands cover FW-to-host Z/S backing, freelist growth/reconstruction, context reset notification, debug dump, stats update, clock rate change, GPU restart request, and FW page fault notification. The one inline helper is `rogue_fwif_compchecks_bvnc_init`.

Control flow: The file describes bidirectional command flow. Host posts kernel CCB (`KCCB`) packets to firmware; KCCB return slots communicate execution, busy cleanup, or poll failure. Clients post CCCB workload packets identified by magic-tagged command types and task bits; the kernel patches protected addresses into shared command prefixes. Firmware posts FWCCB packets back for host services such as memory backing, freelist growth, reset notification, stats update, or restart. HWR flow records fault type, timers, DM, PC/fault addresses, and recovery flags into a circular first/latest buffer. Power and connection control move through explicit enum states.

State and persistence behavior: Most structs live in shared GPU/FW memory and are stateful across command submissions and power transitions. `rogue_fwif_sysdata` persists firmware runtime flags, HWPerf indices/drop counters, fault ring, polling state, HWR flags, and MC configuration. `rogue_fwif_osdata` persists per-OS sync markers, SLR logs, forced update counts, interrupts, executed KCCB count, and power sync address. Runtime config can persist active PM latency when `active_pm_latency_persistant` is set. Context structs persist CCCB addresses, suspend state, priority, lists, stats, wait-signal state, robustness address, memory context, server context ID, PID, and geometry OOM policy. GPU utilization uses a 256-entry timer-correlation ring and accumulators. Freelist/HWRT data persist PM stack pointers, cat bases, freelist snapshots, render-target state, flags, cleanup state, and partial-render lifecycle.

Dependencies and integration points: Includes Linux `bits`, `build_bug`, `compiler`, `kernel`, and `types`, plus `pvr_rogue_defs.h`, `pvr_rogue_fwif_common.h`, and `pvr_rogue_fwif_shared.h`; it pulls in `pvr_rogue_fwif_check.h` for ABI assertions. It integrates with DRM scheduler submission, memory manager/MMU, firmware loader, power manager, HWPerf, debugfs/trace decoding, HWR recovery, sync checkpoint/fence handling, and userspace-visible command streams via client/shared headers.

Risks: ABI drift is the dominant risk. Reordering fields, changing enum widths, altering alignment, or changing command opcodes can break firmware compatibility. Several macros must be treated carefully: command magic detects corruption, GPU-util time/state macros encode state in low bits, and time conversion can overflow if stale correlation entries are used beyond intended windows. Queue offsets require wrap-mask and alignment correctness. Host must not trust userspace-provided FW addresses and must patch shared geom/frag fields. Power/reset/HWR fields are cross-thread and cross-OS synchronization points.

Test signals: The strongest tests are compile-time `pvr_rogue_fwif_check.h` assertions, firmware boot and compatibility checks (`rogue_fwif_compchecks`), KCCB/FWCCB round trips, workload submission for geometry/fragment/compute/TDM/transfer, HWR injection or watchdog tests, freelist OOM/grow/reconstruction tests, Z/S backing tests, HWPerf/counter dump tests, DVFS timer-correlation checks, sync checkpoint state transitions, and suspend/resume or GPU power-cycle loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_check.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_check.h

Purpose: This companion header is the compile-time ABI verifier for `pvr_rogue_fwif.h`. It asserts exact offsets and sizes for FW-shared structures so the host compiler cannot silently produce layouts that differ from firmware expectations.

Important APIs/types/functions: The exported macros are `OFFSET_CHECK(type, member, offset)` and `SIZE_CHECK(type, size)`, both backed by `static_assert`. The checks cover trace buffers, fault records, `rogue_fwif_sysdata`, SLR/OS data, HWR info, memory/context objects, KCCB/FWCCB payloads, runtime configuration, connection and compatibility checks, OS init, signature/counter dump controls, PDVFS OPPs, HWPerf BVNC, system init, GPU utilization control block, RTA control, freelists, HWRT common/data, and sync checkpoint records.

Control flow: None at runtime. Inclusion from `pvr_rogue_fwif.h` causes C compilation to fail if any checked structure layout diverges.

State and persistence behavior: No storage is introduced. The file protects persisted shared-memory layouts by forcing exact binary positions for fields such as queue offsets, fault logs, context addresses, timer correlation state, and freelist/HWRT metadata.

Dependencies and integration points: It depends on `offsetof` availability through included compiler headers and includes `linux/build_bug.h`. It must be included after the relevant structs are declared. It is an integration gate between kernel C ABI, firmware ABI, and generated layout expectations.

Risks: Missing checks allow ABI drift; stale checks block intentional ABI updates until firmware and host are changed together. The assertions also assume compiler enum size and alignment behavior, so toolchain option changes can surface here. Because it checks many large structs, failures should be treated as compatibility issues rather than style problems.

Test signals: Any kernel build including `pvr_rogue_fwif.h` exercises this header. Useful review signals are deliberate offset-change compile failures, CI builds across supported architectures/compilers, and firmware compatibility tests after any FWIF structure edit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_client.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_client.h

Purpose: This header defines client workload command payloads for geometry, fragment, compute, and transfer/TDM work. These layouts are shared with firmware and are partly visible to userspace command generation, while kernel code patches the protected shared prefix for geometry/fragment jobs.

Important APIs/types/functions: Constants include PM sizing (`ROGUE_PM_PAGE_SIZE`, `ROGUE_PM_MAX_FREELIST_SIZE`), geometry flags (`FIRSTKICK`, `LASTKICK`, `SINGLE_CORE`), fragment flags (`SINGLE_CORE`, visibility results, depth/stencil/scratch buffers, disable pixel merge, prevent CDM overlap), compute flags (`PREVENT_ALL_OVERLAP`, `SINGLE_CORE`), and transfer `SINGLE_CORE`. Main structs are `rogue_fwif_geom_regs`, `rogue_fwif_dummy_rgnhdr_init_geom_regs`, `rogue_fwif_cmd_geom`, `rogue_fwif_frag_regs`, `rogue_fwif_cmd_frag`, `rogue_fwif_compute_regs`, `rogue_fwif_cmd_compute`, `rogue_fwif_transfer_regs`, and `rogue_fwif_cmd_transfer`.

Control flow: There is no executable flow, but the data describes submission flow. Geometry commands carry the shared kernel-patched RT/pr-buffer prefix, register programming for VDM/PPP/TE/TPU/PDS, first/last kick flags, partial-render fence, and BRN workaround fields. Fragment commands configure ISP/USC/PBE/ZLS/PDS state and execution count. Compute commands select either user-mode queue or control-stream base paths, context state, TPU/CDM registers, temporary regions, stream start, and multicore execute count. Transfer commands configure ISP/PDS/PBE state for transfer render work.

State and persistence behavior: Instances are stored in client CCB memory and consumed by firmware. The header itself has no state, but its fields become persistent until firmware reads the command and updates associated context/HWRT/fence state. PM freelist constants constrain long-lived parameter memory allocation.

Dependencies and integration points: Includes Linux `bits`, `kernel`, `sizes`, `types`, and `pvr_rogue_fwif_shared.h`; it includes `pvr_rogue_fwif_client_check.h` for layout assertions. It integrates with userspace winsys/UM command streams, kernel bridge validation, CCCB submission, FW task dispatch, PM allocation, partial render handling, and hardware feature/BRN-specific command packing.

Risks: The geometry/fragment shared prefix must remain first so the kernel can safely patch FW addresses without understanding the whole BVNC-specific command. Incorrect field alignment around 64-bit registers breaks firmware reads. Feature-conditional fields must be zero or ignored correctly on GPUs lacking the feature. Freelist size errors can allow PM address wrap/corruption.

Test signals: Compile-time client layout checks, userspace-to-kernel command submission tests, Vulkan/OpenGL geometry and fragment workloads, compute queue tests with and without user-mode queues, transfer/TQ tests, PM OOM/partial-render tests, BRN-specific regression workloads, and command stream fuzzing against `ROGUE_FWIF_DM_INDEPENDENT_KICK_CMD_SIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_client_check.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_client_check.h

Purpose: This header compile-time verifies the binary layout of client command structures from `pvr_rogue_fwif_client.h`.

Important APIs/types/functions: It defines `OFFSET_CHECK` and `SIZE_CHECK` and asserts exact offsets/sizes for `rogue_fwif_geom_regs` (64 bytes), dummy region-header init regs, `rogue_fwif_cmd_geom` (112), `rogue_fwif_frag_regs` (448), `rogue_fwif_cmd_frag` (480), `rogue_fwif_compute_regs` (72), `rogue_fwif_cmd_compute` (96), `rogue_fwif_transfer_regs` (176), and `rogue_fwif_cmd_transfer` (192).

Control flow: None at runtime. Inclusion fails the build if the compiler layout or source fields differ from the expected firmware ABI.

State and persistence behavior: No state. It protects CCCB command payload persistence by verifying register and flag offsets that firmware reads from shared command memory.

Dependencies and integration points: Depends on `linux/build_bug.h` and prior declaration of client FWIF structs. It integrates with CI/build validation for user/kernel/firmware shared command ABI.

Risks: Stale expected offsets block intended ABI updates; missing newly added fields from this file would reduce ABI coverage. Because geometry/fragment command prefixes are security-sensitive kernel patch areas, these checks are a useful guard against accidental prefix movement.

Test signals: Kernel build is the direct signal. Additional confidence comes from intentionally perturbing struct fields in review tests, cross-architecture builds, and end-to-end workload submissions after any client-command change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_client_check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_common.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_common.h

Purpose: This small shared header centralizes FWIF alignment requirements, firmware data-master IDs, GPU utilization state IDs, and register-programmer write limits used by the broader Rogue FWIF ABI.

Important APIs/types/functions: `PVR_FW_ALIGNMENT_LSB` requires low three bits clear for 8-byte granularity. `PVR_FW_STRUCT_SIZE_ASSERT(type)` statically checks ABI struct sizes. Data-master IDs define GP, 2D/TDM, GEOM, FRAG, CDM, RAY, GEOM2-4, `PVR_FWIF_DM_LAST`, and `PVR_FWIF_DM_MAX`. GPU util states are idle, active, blocked, count, and mask. `PVR_MAX_NUM_REGISTER_PROGRAMMER_WRITES` caps firmware/register-programmer write batches at 128.

Control flow: None, apart from compile-time `static_assert` expansion.

State and persistence behavior: No local state. The constants size arrays in persistent shared structs such as HWR recovery flags and utilization counters.

Dependencies and integration points: Depends on `linux/build_bug.h`. Included by central FWIF headers and any code needing stable DM IDs. It integrates with scheduler DM routing, HWR per-DM arrays, utilization accounting, and register programming validation.

Risks: Changing DM numeric values breaks firmware/host interpretation of per-DM state and command routing. A wrong utilization mask corrupts packed time/state words. Weakening alignment checks can hide ABI drift.

Test signals: Build-time assertions, HWR array size checks, GPU utilization accounting tests, and workloads across all supported DMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_dev_info.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_dev_info.h

Purpose: This header enumerates firmware-visible device capability indices for BRNs, ERNs, and hardware features. It is an index contract rather than a value store: arrays or bitsets elsewhere use these enum values to report whether a workaround, enhancement, or feature exists.

Important APIs/types/functions: The BRN enum includes entries such as 44079, 47217, 48492, 48545, 49927, 50767, 51764, 62269, 63142, 63553, 66011, and 71242, ending with `PVR_FW_HAS_BRN_MAX`. The ERN enum includes 35421, 38020, 38748, 42064, 42290, 42606, 47025, and 57596, ending with `PVR_FW_HAS_ERN_MAX`. The feature enum covers major HW capabilities: AXI ACE-lite, CDM control stream format, cluster grouping, compute, FBCDC variants, GPU multicore/virtualization, IRQ per OS, ISP/ZLS/tile parameters, META/MIPS/RISC-V FW processors, number of clusters/OSIDs/raster pipes, SLC sizing/cache line, SOC timer, tessellation, TLA, TPU globals/filtering, USC output registers, VDM features, watchdog, workgroup protection, XE architecture/memory, XPU limits, and more, ending with `PVR_FW_HAS_FEATURE_MAX`.

Control flow: None. Consumer code indexes capability tables with these values.

State and persistence behavior: No state. The enum order is persistent ABI for feature bitmaps passed between host and firmware.

Dependencies and integration points: No includes. It integrates with device info extraction, feature tables, command stream generation, BRN/ERN extension streams, and firmware compatibility checks.

Risks: Reordering or deleting enum entries changes every downstream bit/index interpretation. New capabilities must be appended carefully and paired with table-size updates. Misreported feature bits cause command packing to include missing registers or omit required workaround data.

Test signals: Feature table bounds tests against `*_MAX`, BVNC compatibility tests, command-stream generation on multiple GPU feature sets, and BRN/ERN-specific regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_dev_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_resetframework.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_resetframework.h

Purpose: This header defines the small firmware reset-framework command payload used to preserve or restore compute queue/control-stream registers through reset/context recovery paths.

Important APIs/types/functions: `rogue_fwif_rf_registers` contains a union for either `cdmreg_cdm_cb_base` or `cdmreg_cdm_ctrl_stream_base`, plus `cdmreg_cdm_cb_queue` and `cdmreg_cdm_cb`. `rogue_fwif_rf_cmd` wraps those registers and requires `fw_registers` to be the last member of the containing structure. `ROGUE_FWIF_RF_CMD_SIZE` exposes the payload size.

Control flow: No executable code. The data is prepared by the host or firmware reset framework and then consumed as a block of CDM state registers.

State and persistence behavior: Instances represent persistent reset recovery state in FW-shared memory. The union reflects two mutually exclusive CDM modes: user-mode queue base or control-stream base.

Dependencies and integration points: Includes Linux `bits`/`types` and `pvr_rogue_fwif_shared.h` for shared alignment/types. It integrates with compute context reset, hard context switching, and firmware register replay.

Risks: Adding fields after `fw_registers` violates the documented size/copy assumption. Choosing the wrong union interpretation can restore an invalid CDM queue/control-stream state.

Test signals: Compute HWR/reset tests, context store/resume tests, CDM user-mode queue vs control-stream submissions, and compile/build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_resetframework.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_sf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_sf.h

Purpose: This header is the firmware trace string-format catalog. It maps firmware string-format IDs to host-readable format strings and defines the ID encoding used in firmware trace buffers. It explicitly warns that group/order compatibility must not be broken.

Important APIs/types/functions: `enum rogue_fw_log_sfgroups` defines trace groups: null, main, cleanup, context switch, PM, RTD, SPM, MTS, BIF, misc, power, HWR, HWP, RPM, DMA, and debug. `PVR_SF_STRING_MAX_SIZE` bounds firmware-side strings. `rogue_fw_stid_fmt` and `rogue_km_stid_fmt` describe ID/string pairs. ID macros include `ROGUE_FW_LOG_IDMARKER`, `ROGUE_FW_LOG_CREATESFID(id, group, params)`, `ROGUE_FW_LOG_IDMASK`, `ROGUE_FW_LOG_VALIDID`, `ROGUE_FW_SF_GID`, and `ROGUE_FW_SF_PARAMNUM`. `stid_fmts[]` is the static kernel decode table, with hundreds of entries covering workload kicks, UFO checks/updates, HWR, power, cleanup, context switching, PM/SPM/RTD, HWPerf, DMA, and debug messages. Boundary constants include `ROGUE_FW_SF_FIRST`, `ROGUE_FW_SF_MAIN_ASSERT_FAILED`, and `ROGUE_FW_SF_LAST`.

Control flow: No driver control flow, but trace decoding flow is fixed: firmware writes an encoded SFID and parameters; host validates the ID marker, extracts group and parameter count, looks up the matching `stid_fmts` entry, and formats the trace message.

State and persistence behavior: The static table is read-only kernel data. Its ordering and numeric IDs are persistent firmware trace ABI; historical firmware logs depend on entries retaining their IDs and format parameter counts.

Dependencies and integration points: Uses `u32` types from the including environment. It integrates with `pvr_rogue_fwif.h` trace buffers, debugfs/log decoding, firmware assert reporting, HWR diagnostics, and support tooling that groups logs by the encoded group ID.

Risks: Reordering, deleting, or changing parameter counts breaks decoding of both live and archived firmware traces. Format-string/type mismatches can corrupt log output. The ID uses only four bits for parameter count and group, so new groups/large parameter counts must fit the encoding.

Test signals: Build coverage, trace decoding unit tests for valid/invalid IDs, firmware assert log parsing, HWR trace dumps, and comparison of known firmware trace buffers against expected strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_sf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_shared.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_shared.h

Purpose: This header defines FWIF structures shared by userspace, kernel, and firmware across command submission and context management. It contains the common pieces that remain stable across BVNC-specific geometry/fragment command layouts.

Important APIs/types/functions: Constants set counts for RT data, geometry data, freelists, geometry cores, maximum UFOs, independent DM command size, and partial-render buffer IDs. Core structs include `rogue_fwif_dma_addr`, `rogue_fwif_ufo`, `rogue_fwif_sync_checkpoint`, `rogue_fwif_cleanup_ctl`, `rogue_fwif_cmd_common`, `rogue_fwif_cmd_geom_frag_shared`, `rogue_fwif_cccb_ctl`, `rogue_fwif_geom_registers_caswitch`, `rogue_fwif_cdm_registers_cswitch`, `rogue_fwif_static_rendercontext_state`, `rogue_fwif_static_computecontext_state`, `rogue_fwif_prbuffer`, and `rogue_context_reset_reason_data`. Enums define PR-buffer backing states and context reset reasons including lockup, overrun, HCS, WGP/TRP checksum, ECC, watchdog, FW page fault, execution error, host watchdog, and geometry OOM-disabled.

Control flow: The key described flow is CCCB scheduling: host `write_offset`, firmware `read_offset`, and dependency `dep_offset` partition commands into executing, runnable, and fenced/not-ready ranges. Geometry/fragment commands start with `rogue_fwif_cmd_geom_frag_shared` so the kernel can patch RTData and PR-buffer FW addresses while leaving BVNC-specific payload interpretation to client/FW. Cleanup controls count submitted vs executed commands for resource reclamation. PR buffers move through unbacked, backed, backing pending, and unbacking pending states.

State and persistence behavior: These structs live in shared memory and persist across submissions. CCCB offsets persist queue progress. Cleanup counters persist resource-lifetime handshakes. Static context-switch register images persist render/compute context state. PR buffers persist backing state and cleanup status. Reset reason data persists the last context reset reason and external job reference.

Dependencies and integration points: Includes Linux `compiler`/`types` and its check header. It integrates with `pvr_rogue_fwif_client.h`, `pvr_rogue_fwif.h`, sync/fence handling, command queues, context switch setup, partial render/Z/S/MSAA buffer management, and reset reporting.

Risks: The shared geometry/fragment prefix must remain first and exactly 16 bytes. Queue offsets must be 16-byte aligned and wrap-mask consistent. UFO address tagging (`ROGUE_FWIF_UFO_ADDR_IS_SYNC_CHECKPOINT`) means consumers must distinguish sync checkpoints from sync prims. Typo-like field `cleanup_sate` is ABI and should not be renamed without coordinated firmware changes.

Test signals: Compile-time shared layout checks, CCCB wrap/fence tests, geometry/fragment submission through kernel patching, sync checkpoint fence merge tests, PR buffer on-demand backing/unbacking, and HWR reset reason propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_shared_check.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_shared_check.h

Purpose: This header verifies the exact binary layout of shared FWIF structs from `pvr_rogue_fwif_shared.h`.

Important APIs/types/functions: `OFFSET_CHECK` and `SIZE_CHECK` assert `rogue_fwif_dma_addr` (16 bytes), `rogue_fwif_ufo` (8), `rogue_fwif_cleanup_ctl` (8), `rogue_fwif_cccb_ctl` (32), `rogue_fwif_geom_registers_caswitch` (184), `rogue_fwif_cdm_registers_cswitch` (56), static render/compute context states (368/56), `rogue_fwif_cmd_common` (4), and `rogue_fwif_cmd_geom_frag_shared` (16).

Control flow: None at runtime. Inclusion makes ABI drift a compile-time error.

State and persistence behavior: No state. It protects the queue/control/context-switch structures that persist in shared memory.

Dependencies and integration points: Depends on `linux/build_bug.h` and prior shared struct declarations. It is included by `pvr_rogue_fwif_shared.h` and therefore indirectly by client and core FWIF headers.

Risks: If a shared struct changes without updating firmware and this file, builds fail. If new shared structs are added but not checked, drift can escape. The geometry/fragment shared-prefix check is particularly important for security and cross-BVNC submission.

Test signals: Kernel build, cross-compiler build, and deliberate layout-change compile-failure checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_shared_check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_stream.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_stream.h

Purpose: This header documents and defines the command stream extension-header format used when userspace submits Rogue commands to the kernel. It separates fixed main-stream data from optional BRN/ERN extension data.

Important APIs/types/functions: Header fields are `PVR_STREAM_EXTHDR_TYPE_SHIFT`, `PVR_STREAM_EXTHDR_TYPE_MASK`, `PVR_STREAM_EXTHDR_TYPE_MAX`, `PVR_STREAM_EXTHDR_CONTINUATION`, and `PVR_STREAM_EXTHDR_DATA_MASK`. Per-DM extension type/valid masks currently define geometry type 0 with BRN49927, fragment type 0 with BRN47217/BRN49927 but valid mask only BRN49927, and compute type 0 with BRN49927.

Control flow: Parsing flow is specified in comments: a command stream starts with a 64-bit length/padding header, then main stream data, then optional extension headers and extension payloads. Each extension header carries type, continuation, and quirk/enhancement bitmask; parsing continues while the continuation bit is set. Extension parameters override duplicate main-stream parameters.

State and persistence behavior: The header has no state. Parsed stream data becomes transient submission data and may be copied into persistent client CCB command structs.

Dependencies and integration points: No includes in the file itself; it assumes `BIT` is available via inclusion context. It integrates with userspace command builders, kernel stream parsers/validators, `pvr_rogue_fwif_dev_info.h` BRN/ERN capability indices, and client command structs.

Risks: Parser and producer must agree on natural alignment and reserved-zero bits. The fragment valid mask excluding BRN47217 despite defining the bit is a compatibility detail that should be reviewed before enabling. Bad length or continuation handling can overrun streams or ignore required workaround data.

Test signals: Stream parser unit tests for main-only, single-extension, multi-header continuation, reserved bits, invalid type, duplicate override behavior, natural alignment, and BRN49927/BRN47217 feature-specific command packing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_heap_config.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_heap_config.h

Purpose: This header defines the Rogue device virtual address heap map used by application memory contexts and firmware/kernel-only allocations. It is a layout contract for userspace-visible heaps and global execution base programming.

Important APIs/types/functions: Exports heap base/size constants: `ROGUE_GENERAL_HEAP_BASE/SIZE` at 512-640 GiB, `ROGUE_PDSCODEDATA_HEAP_BASE/SIZE` at 872-876 GiB, `ROGUE_RGNHDR_HEAP_BASE/SIZE` at top of a 16 GiB range for BRN63142, `ROGUE_USCCODE_HEAP_BASE/SIZE` at 896-900 GiB, `ROGUE_FW_HEAP_BASE` in the reserved firmware region, `ROGUE_TRANSFER_FRAG_HEAP_BASE/SIZE`, and `ROGUE_VISTEST_HEAP_BASE/SIZE`. There are no functions or structs.

Control flow: None. Allocation code selects heaps based on buffer purpose and uses these ranges to configure GPU virtual memory and global PDS/USC execution bases.

State and persistence behavior: The header has no state, but heap base choices persist as ABI-visible virtual addresses in memory contexts. Firmware heap placement is kernel-only and should not be exposed to userspace.

Dependencies and integration points: Includes `linux/sizes.h`. Integrates with DRM GEM/device memory managers, userspace VA allocation, PDS/USC code upload, region header allocation, transfer/fragment resources, visibility tests, and firmware memory setup.

Risks: Overlapping or moving heaps breaks userspace ABI and can corrupt GPU VA mappings. Bases must remain 4 MiB aligned and avoid zero. The BRN63142 region-header placement is a workaround-sensitive constraint. Comments show some free/reserved region ranges and sizes that should be checked carefully when extending the map.

Test signals: VA allocator tests for every heap, overlap/alignment assertions, userspace mmap/bind tests, PDS/USC execution tests, region-header BRN63142 regression, firmware heap isolation tests, and memory-context creation across 40-bit VA boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_heap_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_meta.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_meta.h

Purpose: This header defines META firmware processor registers, loader block formats, segmented MMU setup constants, bootloader defaults, stack/coremem regions, and META compatibility IDs. It is used by firmware loading/bootstrap and low-level debug/control paths for Rogue variants using META firmware processors.

Important APIs/types/functions: Register helpers include `META_CR_CTRLREG_BASE`, privilege/JTAG registers, perf counter registers and selectors, core register access request/data offsets, thread PC/SP access macros, thread enable/status/DEFR/privilege offsets, clock control, local cache partition/cache control registers, and segment MMU register address macros. Loader structs are `rogue_meta_ldr_block_hdr`, `rogue_meta_ldr_l1_data_blk`, `rogue_meta_ldr_l2_data_blk`, and `rogue_meta_ldr_cfg_blk`; command constants cover load memory/core/MMREG, start threads, zero memory, and config commands. SegMMU constants define thread/write permissions, direct-map GPU region, data/bootloader/text segment IDs, SLC/cache output address macros, alignment, data base/cache policy encodings, bootloader META/device addresses and limits, bootloader config offset, stack size, coremem code/data address detection macros, second-thread PC/SP defaults, core ID/version fields, known META core ID values, and `ROGUE_FW_PROCESSOR_META`.

Control flow: The header encodes bootstrap flow rather than executing it. Loader code parses L1/L2/config blocks, loads memory/registers, configures segmented MMU windows, maps firmware data/code/bootloader areas, sets thread PC/SP, and enables META threads. Debug code can read PC/SP via TXUXXRX request/data registers and poll `DREADY`.

State and persistence behavior: No C storage. Constants define persistent META register state during firmware boot and runtime: privilege mode, cache partitioning, segment base/limit/out address, bootloader memory mapping, stack placement, and performance counter selection.

Dependencies and integration points: Includes Linux `bits` and `types`. Integrates with firmware image parser, bootloader copier, segmented MMU setup, coremem detection, FW processor compatibility checks, perf/debug tracing, and any code that supports META alongside MIPS/RISC-V FW processors.

Risks: Manual register definitions can drift from hardware docs. Several macros are low-level and unforgiving: wrong segment output address bits can make firmware fetch from the wrong memory/cacheability domain; wrong bootloader address/limit can overwrite invalid memory; wrong PC/SP defaults prevent thread startup. `META_CR_PERF_COUNT_THR_1` appears to shift by `META_CR_PERF_COUNT_THR_1` instead of `META_CR_PERF_COUNT_THR_SHIFT`, which is worth review because it likely expands incorrectly if used. `META_CR_PERF_COUNT(ctrl, thr)` also combines already-shifted selector macros with another shift pattern and should be checked against intended usage.

Test signals: Firmware boot on META cores, loader command parsing tests, segment MMU programming trace comparison, coremem address classification tests, thread start/PC/SP readback tests, cache policy validation, and META core ID compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_meta.h -->
