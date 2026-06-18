# subset-b-003777 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_topology.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_topology.c

## Purpose

`xe_gt_topology.c` discovers and reports the fused hardware topology for an Xe GT. It reads DSS geometry/compute masks, EU mask/type, and L3 bank masks from platform-specific fuse registers, stores the normalized values in `gt->fuse_topo`, and provides query helpers used by steering, engine enablement, userspace topology reporting, and debug output.

## Important APIs, Types, and Functions

- `xe_gt_topology_init()` is the initialization entry point. It loads geometry and compute DSS masks, EU mask/type, L3 bank mask, then dumps the result through the GT debug printer.
- `load_dss_mask()` reads one or more 32-bit fuse registers and converts them into `xe_dss_mask_t`.
- `load_eu_mask()` normalizes EU enable bits across pre-Xe_HP inverted semantics and SIMD8/SIMD16 encodings.
- `load_l3_bank_mask()` translates platform-specific L3 fuse layouts into `xe_l3_bank_mask_t`.
- `gen_l3_mask_from_pattern()` expands per-node/per-mask-bit patterns according to an enable mask.
- Query helpers include `xe_gt_topology_report_l3()`, `xe_gt_topology_dump()`, `xe_dss_mask_group_ffs()`, `xe_l3_bank_mask_ffs()`, `xe_gt_topology_has_dss_in_quadrant()`, `xe_gt_has_geometry_dss()`, `xe_gt_has_compute_dss()`, and `xe_gt_has_discontiguous_dss_groups()`.

## Control Flow

Initialization begins with fixed arrays of geometry and compute fuse registers. The function asserts that GT metadata does not request more registers than the arrays provide, reads the requested register count, and converts the raw arrays into bitmaps. EU loading reads `XELP_EU_ENABLE`, adjusts bit polarity for older platforms, expands SIMD8 encoding when one bit represents two EUs, and records `XE_GT_EU_TYPE_SIMD8` or `XE_GT_EU_TYPE_SIMD16`. L3 loading first suppresses media-GT L3 reporting on Xe3+ where the media mask is known unreliable, then handles Xe3.5+, Xe3, Xe2, Xe_HP/Xe_HPC/PVC/DG2, and older inverted one-bit-per-bank formats.

## State and Persistence Behavior

The file writes persistent topology state into `struct xe_gt::fuse_topo`. The masks are cached for later driver decisions and reporting; there is no allocation, reference counting, or delayed work. It assumes GT MMIO is readable during init and does not refresh topology after initialization.

## Dependencies and Integration Points

It depends on GT MMIO access, platform version macros, register definitions, bitmap helpers, MCR steering iteration, GT assertions, and workaround metadata. Consumers include topology dump/reporting paths, CCS quadrant enablement, MCR steering selection, L3 topology ABI reporting, and tests or debugfs that inspect GT topology.

## Risks and Edge Cases

The platform-specific L3 normalization is easy to break when register definitions change. The DSS quadrant helper divides by four based on the larger geometry/compute fuse-register span, so malformed metadata can produce misleading quadrant decisions. Media GT L3 reporting is ABI-sensitive because pre-Xe3 behavior is preserved even though values may be bogus. `xe_gt_has_*_dss()` trusts callers not to query beyond the bitmap width.

## Test Signals

Useful tests mock fuse register values for each platform branch, verify SIMD8 expansion and SIMD16 direct mapping, assert media GT L3 suppression on Xe3+, cover empty DSS and L3 masks, and check quadrant/discontiguous helpers against synthetic masks. Runtime signals include debug topology dumps and userspace topology queries matching expected fuse data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_topology.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_topology.h

## Purpose

`xe_gt_topology.h` exposes the GT topology initialization and query interface. It also defines the canonical DSS iteration macro that combines geometry and compute DSS masks.

## Important APIs, Types, and Functions

- `for_each_dss(dss, gt)` iterates set bits in the OR of `gt->fuse_topo.g_dss_mask` and `gt->fuse_topo.c_dss_mask`.
- `xe_gt_topology_init()` fills `gt->fuse_topo`.
- `xe_gt_topology_dump()` prints cached topology through a `drm_printer`.
- `xe_gt_topology_mask_last_dss()` returns `find_last_bit()` or `XE_MAX_DSS_FUSE_BITS` for an empty mask.
- `xe_dss_mask_group_ffs()` and `xe_l3_bank_mask_ffs()` find first set DSS/L3 entries.
- `xe_gt_topology_has_dss_in_quadrant()`, `xe_gt_has_geometry_dss()`, `xe_gt_has_compute_dss()`, `xe_gt_has_discontiguous_dss_groups()`, and `xe_gt_topology_report_l3()` provide higher-level queries.

## Control Flow

The header is declarative apart from inline helpers. Its control-flow contract is that callers initialize topology once with `xe_gt_topology_init()` before iterating or querying masks. `for_each_dss()` relies on Linux bitmap OR iteration and the fixed `XE_MAX_DSS_FUSE_BITS` width defined in `xe_gt_types.h`.

## State and Persistence Behavior

No state is stored in the header. It exposes access to persistent masks held by `struct xe_gt`. Callers that cache results must account for the fact that this interface does not provide invalidation or re-read hooks.

## Dependencies and Integration Points

It includes `xe_gt_types.h` for `struct xe_gt`, mask typedefs, and topology widths. The API is used by topology initialization, MCR steering, engine/CCS configuration, debug dumping, and code that needs to know whether an individual DSS exists for geometry or compute.

## Risks and Edge Cases

`for_each_dss()` intentionally iterates DSS available to either geometry or compute; callers needing only one domain must use `xe_gt_has_geometry_dss()` or `xe_gt_has_compute_dss()`. `xe_gt_topology_mask_last_dss()` returns the bitmap size for empty masks, which callers must not treat as a valid DSS index.

## Test Signals

Compile coverage catches signature drift. Unit tests should cover empty masks, combined geometry/compute iteration, and the distinction between any-DSS iteration and per-domain queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_types.h

## Purpose

`xe_gt_types.h` defines the central `struct xe_gt` and related enums, masks, and conversion helpers for an Xe Graphics Technology unit. It is the shared data contract for GT initialization, topology, power management, GuC/uC, engines, workarounds, steering, user-visible engine availability, OA, and stall tracking.

## Important APIs, Types, and Functions

- `enum xe_gt_type` distinguishes uninitialized, main, and media GTs.
- `enum xe_gt_eu_type` records SIMD8 versus SIMD16 EU mask encoding.
- `XE_MAX_DSS_FUSE_*`, `XE_MAX_EU_FUSE_*`, and `XE_MAX_L3_BANK_MASK_BITS` define topology bitmap widths.
- `xe_dss_mask_t`, `xe_eu_mask_t`, and `xe_l3_bank_mask_t` are fixed-width bitmap types used by topology code and ABI reporting.
- `enum xe_steering_type` classifies MCR steering categories, from L3BANK/DSS/node-specific steering to implicit/default steering.
- `gt_to_tile()` and `gt_to_xe()` are `_Generic` helpers preserving constness.
- `struct xe_gt` aggregates backpointers, hardware identity, MMIO, forcewake, SR-IOV state, register save/restore, reset work, TLB invalidation, CCS mode, USM state, workqueues, `struct xe_uc`, idle state, submission ops, hardware engines, sysfs nodes, MOCS, fuse topology, steering targets, locks, workaround/tuning bitmaps, user engine exposure, OA, and EU stall data.

## Control Flow

This header does not execute runtime logic, but it defines the storage that many init flows progressively populate: device/tile setup creates GTs; topology code fills `fuse_topo`; engine discovery fills `hw_engines`, `eclass`, and engine masks; GuC initialization fills `uc`; power and reset paths use locks/workqueues; sysfs/debug paths read the resulting state.

## State and Persistence Behavior

`struct xe_gt` is long-lived for a GT instance. Many fields are persistent hardware facts (`info`, `fuse_topo`, `mmio`), while others are runtime mutable (`reset.worker`, `tlb_inval`, `uc`, forcewake, workaround bitmaps, user engine masks). The type itself does not enforce locking; individual subsystems document and protect their own fields.

## Dependencies and Integration Points

The header pulls in major subsystem type headers: device, forcewake, idle, SR-IOV PF/VF, stats, hardware engines/fences, OA, register save/restore, suballocation, TLB invalidation, and uC. It is included by most GT, GuC, engine, topology, reset, and debug modules.

## Risks and Edge Cases

Because `struct xe_gt` is broad and shared, field lifetime and locking assumptions are easy to violate. The const-preserving `_Generic` helpers depend on exact pointer types. Topology widths are ABI-relevant; changing them affects bitmap storage and reporting. MCR steering categories must stay synchronized with platform register range tables.

## Test Signals

Build coverage across GT/GuC/engine modules is the primary signal. Structural tests should verify topology bitmap widths, const helper behavior, engine mask/user engine consistency, and reset/power paths that use mutable GT state under the intended locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guard.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guard.h

## Purpose

`xe_guard.h` provides a small spinlock-protected guard primitive for feature exclusion. It is designed for coarse feature state arbitration where a feature can be either in exclusive active use or locked down by one or more blockers, without imposing strict owner semantics like an rwsem.

## Important APIs, Types, and Functions

- `struct xe_guard` contains `counter`, debug `name`, last `owner`, and a `spinlock_t`.
- `xe_guard_init()` initializes the spinlock, clears the counter, and records the name.
- `xe_guard_arm(guard, lockdown, who)` enters lockdown mode when `lockdown` is true or exclusive mode when false.
- `xe_guard_disarm(guard, lockdown)` releases a lockdown reference or exclusive reference and detects mismatches.
- `xe_guard_mode_str()` maps a mode flag to `"lockdown"` or `"exclusive"`.

## Control Flow

The counter encodes state: zero means idle, negative means exclusive active, positive means locked down. Lockdown arm fails with `-EBUSY` if exclusive mode is active and otherwise increments the counter. Exclusive arm fails with `-EPERM` if locked down, `-EUSERS` if already exclusive, and otherwise decrements to `-1`. Disarm validates the mode and moves the counter back toward zero.

## State and Persistence Behavior

State persists in the caller-owned `struct xe_guard`. `owner` is debug-only and records the latest successful armer; it is not cleared on disarm. All counter updates are serialized with the guard spinlock through the kernel cleanup-style `guard(spinlock)` helper.

## Dependencies and Integration Points

It depends on Linux spinlock and cleanup guard helpers, errno values, and boolean types from kernel headers. It is appropriate for feature-gating paths where lockdown and activation are incompatible but no data payload is protected.

## Risks and Edge Cases

The comments explicitly warn not to use this for data protection; it does not provide reader/writer ownership or memory lifetime semantics. Multiple lockdowns are allowed but each must be disarmed. The `owner` field can be stale after release. Error-code distinctions matter to callers that need to report "locked down" versus "already active".

## Test Signals

Tests should cover idle-to-lockdown nesting, idle-to-exclusive, lockdown blocking exclusive, exclusive blocking lockdown, double-exclusive returning `-EUSERS`, mismatched disarms returning false, and balanced disarms returning to zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc.c

## Purpose

`xe_guc.c` is the main lifecycle and command glue for the GuC microcontroller. It initializes firmware metadata and GuC subsystems, builds GuC boot parameters, uploads firmware, enables communication, handles reset/suspend/resume, provides MMIO and CT command helpers, manages optional GuC-to-GuC buffers, and exposes diagnostic printing and wedging behavior.

## Important APIs, Types, and Functions

- Initialization: `xe_guc_comm_init_early()`, `xe_guc_init_noalloc()`, `xe_guc_init()`, `xe_guc_init_post_hwconfig()`, `xe_guc_post_load_init()`.
- Firmware load: `xe_guc_min_load_for_hwconfig()`, `xe_guc_upload()`, `__xe_guc_upload()`, `guc_write_params()`, `guc_prepare_xfer()`, `guc_xfer_rsa()`, `guc_wait_ucode()`.
- Reset/power: `xe_guc_reset()`, `xe_guc_suspend()`, `xe_guc_softreset()`, `xe_guc_runtime_suspend()`, `xe_guc_runtime_resume()`, `xe_guc_sanitize()`, `xe_guc_declare_wedged()`.
- Communication: `xe_guc_enable_communication()`, `xe_guc_notify()`, `xe_guc_mmio_send_recv()`, `xe_guc_mmio_send()`, `xe_guc_self_cfg32()`, `xe_guc_self_cfg64()`, `xe_guc_irq_handler()`.
- Feature and setup helpers: `guc_ctl_*()` parameter builders, `xe_guc_opt_in_features_enable()`, G2G allocation/registration helpers, `xe_guc_using_main_gamctrl_queues()`, and `xe_guc_print_info()`.

## Control Flow

Early init selects the host interrupt register and initializes CT/relay. Normal PF init loads GuC firmware metadata, initializes log, capture, ADS, and CT, marks firmware loadable, registers managed cleanup, and writes minimal params. SR-IOV VF init follows a separate bootstrap/config-query path and initializes only the VF-relevant CT/submission pieces. The driver performs a minimal upload to read hwconfig, then post-hwconfig reallocates DGFX BOs to VRAM, initializes CT, submission, doorbells, PC/RC/activity, buffer cache, and ADS. Full upload populates ADS, optionally selects main GAMCTRL queues, writes params into soft scratch registers, programs transfer registers, supplies RSA data, DMA-loads ucode, and polls `GUC_STATUS` until ready or terminal failure.

## State and Persistence Behavior

Persistent GuC state lives in `struct xe_guc`: firmware object, params array, log/ADS/CT/submission/PC/RC/buffer-cache state, notify register, and optional G2G BO. Firmware status transitions through loadable, running, load fail, and sanitized states. Managed device actions clean up hardware state or VF state. Runtime suspend pauses submission, disables it, and disables CT; resume re-enables IRQ/CT/submission and unpauses.

## Dependencies and Integration Points

This file integrates nearly every GuC-facing subsystem: firmware loader, WOPCM, MMIO/forcewake, ADS, capture, CT, log, hwconfig, submission, DB manager, PC/RC, relay, page/memirq, SR-IOV PF/VF migration, GT reset, throttling, workarounds, and configfs. Hardware register definitions and GuC ABI headers define parameter, action, and status formats.

## Risks and Edge Cases

Boot parameter correctness is version/platform-sensitive. `xe_guc_mmio_send_recv()` must handle lost scratch registers during FLR, busy replies, retry replies, migration rejection, and protocol corruption. The minimal-load and full-load stages share state but have different ADS/submission expectations. G2G support is mostly dormant because `xe_guc_g2g_wanted()` returns false. Reset and suspend paths must avoid leaving CT/submission enabled against dead firmware.

## Test Signals

KUnit coverage exists for G2G under `CONFIG_DRM_XE_KUNIT_TEST`. Additional signals include fault injection on init/upload paths, mocked MMIO send responses for success/busy/retry/failure/lost-FLR/protocol cases, firmware load status decoding tests, suspend/resume sequencing tests, SR-IOV VF bootstrap/migration paths, and integration runs verifying GuC status/debugfs output after load and reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc.h

## Purpose

`xe_guc.h` is the public GuC interface for the Xe driver. It exposes lifecycle, upload, reset, communication, self-configuration, IRQ, diagnostic, and helper APIs plus version-comparison macros and engine-class conversion helpers.

## Important APIs, Types, and Functions

- Version macros: `MAKE_GUC_VER()`, `MAKE_GUC_VER_STRUCT()`, `MAKE_GUC_VER_ARGS()`, `GUC_SUBMIT_VER()`, `GUC_FIRMWARE_VER()`, and `GUC_FIRMWARE_VER_AT_LEAST()`.
- Lifecycle/upload APIs mirror `xe_guc.c`: init, post-hwconfig, post-load, reset, upload, min-load, communication enable, suspend/resume, sanitize, stop/start, reset prepare/wait, and wedging.
- Command APIs: `xe_guc_auth_huc()`, `xe_guc_mmio_send*()`, `xe_guc_self_cfg32/64()`, and notification/IRQ helpers.
- Inline helpers convert engine classes to GuC classes and derive `xe_gt`, `xe_device`, and `drm_device` from `struct xe_guc`.

## Control Flow

The header defines the orderable API surface used by GT/uC initialization code: early communication init precedes MMIO messages; noalloc/init/post-hwconfig prepare memory and subsystems; upload starts firmware; communication enable starts CT; post-load enables opt-ins and submission. Inline version checks gate feature setup across implementation files.

## State and Persistence Behavior

No state is owned here. The helpers expose state in `struct xe_guc`, especially firmware version arrays, GT backpointers, and the `uc.guc` placement inside `struct xe_gt`.

## Dependencies and Integration Points

It includes `xe_gt.h`, `xe_guc_types.h`, hardware engine types, and local macro helpers. It is consumed by ADS, CT, capture, HuC auth, submission, reset, debug, and power-management modules.

## Risks and Edge Cases

`xe_engine_class_to_guc_class()` returns `-1` as a `u16` on invalid input after warning, so callers must not treat invalid classes as usable. Version macros rely on 8-bit components and compile-time argument selection; misuse with too many or too few arguments intentionally build-fails.

## Test Signals

Build coverage catches prototype drift. Unit tests should verify class mapping, invalid class warnings, version macro packing, `GUC_FIRMWARE_VER_AT_LEAST()` thresholds, and caller ordering assumptions in init/upload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ads.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ads.c

## Purpose

`xe_guc_ads.c` builds and populates the GuC Additional Data Structures blob. The ADS is a single pinned mapped BO containing the GuC ADS header, scheduler policies, GT system info, engine usage, UM queue parameters, MMIO save/restore regsets, golden LRCs, workaround KLVs, capture lists, UM queues, and firmware private data.

## Important APIs, Types, and Functions

- `xe_guc_ads_init()` computes pre-hwconfig worst-case sizes and allocates the ADS BO.
- `xe_guc_ads_init_post_hwconfig()` recalculates sizes after engine discovery and asserts they fit the original allocation slack.
- `xe_guc_ads_populate_minimal()` writes enough ADS state for minimal GuC load and hwconfig retrieval.
- `xe_guc_ads_populate()` writes full policies, engine masks, regsets, golden LRC addresses, mapping table, capture lists, doorbell info, workaround KLVs, UM queues, and ADS pointers.
- `xe_guc_ads_populate_post_load()` copies captured default LRC images into the ADS.
- `xe_guc_ads_scheduler_policy_toggle_reset()` sends an updated policy buffer over CT.
- Static helpers calculate region sizes/offsets, write regsets, populate capture-list pointers, and build workaround KLVs.

## Control Flow

The ADS layout starts with fixed structs and then page-aligns dynamic regions. Init calculates golden LRC, capture, regset, and workaround sizes, then allocates a BO with extra golden-LRC slack. Minimal population zeroes the BO and writes policies, invalid mapping, golden context addresses, doorbell count, and key ADS pointers. Full population zeroes again, fills engine masks from discovered hardware engines, serializes save/restore MMIO registers including MCR steering metadata, prepares capture lists, writes workaround KLVs, initializes UM queue parameters if USM is supported, and points GuC ADS fields at GGTT offsets.

## State and Persistence Behavior

Persistent ADS metadata lives in `struct xe_guc_ads` and the BO contents consumed by GuC firmware. The BO is managed and pinned for the GuC lifetime. Population is destructive because it clears the whole BO before rebuilding. Scheduler policy toggling uses a temporary GuC buffer cache allocation and does not rewrite the main ADS in place except for reading defaults.

## Dependencies and Integration Points

This file integrates GuC ABI structures, hardware engine lists, register save/restore xarrays, LRC sizing/default LRC data, capture-list generation, MCR steering, workarounds, UM/page-response queues, GGTT BO mapping, CT commands, and GT/DRM logging.

## Risks and Edge Cases

Offset/size arithmetic is ABI-critical. Post-hwconfig size growth relies on `MAX_GOLDEN_LRC_SIZE` slack. Capture-list population logs overflow but continues by writing null lists when unavailable. Workaround KLV buffer size is fixed to one page and excess KLVs only warn. Regset sizing includes slack; missing a new extra register can overflow assertions.

## Test Signals

Tests should validate region offsets/alignment, minimal versus full ADS pointer fields, engine enable masks, mapping-table invalid values, regset counts, MCR steering flags, capture-list size accounting, KLV population under workaround combinations, and policy-toggle CT payloads. Fault injection on ADS allocation is already enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ads.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ads.h

## Purpose

`xe_guc_ads.h` declares the public ADS lifecycle and policy API used by GuC initialization and runtime scheduler policy changes.

## Important APIs, Types, and Functions

- `xe_guc_ads_init()` allocates and sizes ADS storage before hwconfig is available.
- `xe_guc_ads_init_post_hwconfig()` recalculates size requirements after hwconfig and engine discovery.
- `xe_guc_ads_populate_minimal()` writes the minimal ADS needed for early GuC load.
- `xe_guc_ads_populate()` writes the full ADS for normal GuC upload/submission.
- `xe_guc_ads_populate_post_load()` fills data that is only available after GuC/submission initialization, notably golden LRC contents.
- `xe_guc_ads_scheduler_policy_toggle_reset()` updates GuC scheduler reset policy.

## Control Flow

Callers use this interface in phases: init allocation, minimal populate for hwconfig, post-hwconfig recalculation, full populate before firmware upload, post-load populate after default LRCs are captured, and optional runtime policy update through CT.

## State and Persistence Behavior

The header only forward-declares `struct xe_guc_ads`; state is defined in `xe_guc_ads_types.h` and owned by `struct xe_guc`. The functions mutate persistent ADS BO contents and metadata.

## Dependencies and Integration Points

It depends only on Linux types and a forward declaration, keeping ADS callers decoupled from the GuC ABI layout. It is included by `xe_guc.c` and other GuC/submission policy paths.

## Risks and Edge Cases

The phased API is order-sensitive. Calling full populate before post-hwconfig sizing or post-load populate before default LRCs exist can assert or produce invalid firmware data.

## Test Signals

Initialization integration tests should check call ordering and error propagation. Policy tests should verify reset enable/disable requests are reflected in CT actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ads_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ads_types.h

## Purpose

`xe_guc_ads_types.h` defines the small persistent state object for GuC ADS allocation and sizing.

## Important APIs, Types, and Functions

- `struct xe_guc_ads::bo` points to the pinned BO containing the ADS blob.
- `golden_lrc_size` stores total page-aligned golden context storage needed for enabled engine classes.
- `regset_size` stores MMIO save/restore regset bytes.
- `ads_waklv_size` stores workaround KLV region size.
- `capture_size` stores GuC capture-list input storage size.

## Control Flow

The type is filled by `xe_guc_ads_init()` and recalculated by `xe_guc_ads_init_post_hwconfig()`. Population code uses these fields to compute ADS region offsets.

## State and Persistence Behavior

All fields are persistent for the GuC object lifetime. Size fields represent current platform/engine assumptions and are consumed by offset helpers each time the ADS is populated.

## Dependencies and Integration Points

The type forward-declares `struct xe_bo` and is embedded in `struct xe_guc`. It bridges GuC lifecycle code and ADS layout code without exposing GuC ABI internals.

## Risks and Edge Cases

If size fields are stale after hwconfig changes, later population may write incorrect offsets. `bo` must be valid before any populate call. `regset_size` and `capture_size` must be large enough for dynamic MCR/capture content.

## Test Signals

Tests should verify sizes before and after hwconfig, valid BO allocation, and consistency between size fields and populated ADS offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ads_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_buf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_buf.c

## Purpose

`xe_guc_buf.c` implements a reusable GuC data-buffer cache backed by an `xe_sa_manager`. It lets GuC code reserve small temporary GGTT-addressable buffers for command payloads, copy data to/from them, and release suballocations without creating ad hoc BOs.

## Important APIs, Types, and Functions

- `xe_guc_buf_cache_init()` creates the default 8 KiB cache.
- `xe_guc_buf_cache_init_with_size()` creates at least the default size and can grow for larger users.
- `xe_guc_buf_cache_dwords()` returns available cache capacity.
- `xe_guc_buf_reserve()` reserves a dword-sized suballocation with `GFP_ATOMIC`.
- `xe_guc_buf_from_data()` reserves and copies caller data into the buffer.
- `xe_guc_buf_release()` frees a valid suballocation.
- `xe_guc_buf_sync_read()`, `xe_guc_buf_flush()`, `xe_guc_buf_cpu_ptr()`, and `xe_guc_buf_gpu_addr()` expose synchronization, CPU pointer, and GPU address operations.
- `xe_guc_cache_gpu_addr_from_ptr()` maps a CPU pointer inside the cache back to its GPU address.

## Control Flow

Cache initialization finds the owning GuC/GT through container helpers and creates a suballocation BO manager with 32-bit alignment. Reserve paths allocate from the manager or return `-EOPNOTSUPP` if absent. Flush/sync helpers delegate to `xe_sa_bo_*` functions. Release is safe for invalid handles through `xe_guc_buf_is_valid()` in the header.

## State and Persistence Behavior

The cache owns a persistent `xe_sa_manager *sam`; individual `struct xe_guc_buf` values are short-lived references to suballocations. The cleanup class in the header enables scope-bound release. Buffer contents persist until overwritten or released, and explicit flush/sync calls are needed for GPU/CPU visibility.

## Dependencies and Integration Points

It depends on Xe BO/suballocation helpers, GuC/GT backpointers, managed allocation, and GT logging. Users include GuC opt-in feature KLVs, ADS policy updates, and SR-IOV migration payloads.

## Risks and Edge Cases

Reservations use `GFP_ATOMIC`, so allocation failure must be handled. `xe_guc_buf_from_data()` assumes `cache->sam` is initialized. `xe_guc_cache_gpu_addr_from_ptr()` performs pointer arithmetic against the cache base and returns zero for unrelated pointers; callers must treat zero as failure, not a valid address.

## Test Signals

KUnit coverage is included when built in. Tests should cover init sizing, reservation/release, invalid cache behavior, data copy/flush/sync, pointer-to-GPU lookup boundaries, and cleanup-class release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_buf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_buf.h

## Purpose

`xe_guc_buf.h` declares the GuC buffer-cache API and defines cleanup-class helpers for automatic suballocation release.

## Important APIs, Types, and Functions

It exposes cache init, reserve/from-data, release, CPU/GPU pointer, flush/sync, capacity, pointer-to-address lookup, and the inline `xe_guc_buf_is_valid()`. `DEFINE_CLASS(xe_guc_buf, ...)` and `DEFINE_CLASS(xe_guc_buf_from_data, ...)` provide kernel cleanup-scope wrappers.

## Control Flow

Callers initialize a cache, reserve a `struct xe_guc_buf`, check validity, write/read data via CPU pointer, flush before passing GPU address to GuC, and release explicitly or through the cleanup class.

## State and Persistence Behavior

The header itself has no state. It operates on `struct xe_guc_buf_cache` and `struct xe_guc_buf` from `xe_guc_buf_types.h`.

## Dependencies and Integration Points

It depends on Linux cleanup/err helpers and GuC buffer types. It is used by GuC feature opt-ins, ADS policy updates, and any GuC command path needing temporary firmware-visible memory.

## Risks and Edge Cases

The documentation typo says `ref`/`sub-allication`, but the semantic contract is clear. Callers must not dereference CPU/GPU helpers on invalid buffers. Cleanup-class users must ensure the cache outlives the scoped buffer.

## Test Signals

Compile tests should cover cleanup-class use. Runtime/KUnit tests should validate invalid handles, automatic release, and flush-before-GPU-address patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_buf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_buf_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_buf_types.h

## Purpose

`xe_guc_buf_types.h` defines opaque public structs for the GuC buffer cache and individual buffer references.

## Important APIs, Types, and Functions

- `struct xe_guc_buf_cache` contains the internal `struct xe_sa_manager *sam`.
- `struct xe_guc_buf` contains the internal `struct drm_suballoc *sa`.

## Control Flow

There is no executable flow. The types are manipulated only through `xe_guc_buf.h`/`.c` helpers.

## State and Persistence Behavior

The cache manager persists for the GuC lifetime or until device-managed cleanup. Buffer references are transient suballocations and must be released. The fields are marked private by comment but remain visible to C callers.

## Dependencies and Integration Points

It forward-declares DRM suballocation and Xe suballocation manager types, minimizing dependencies for headers that only need buffer handles.

## Risks and Edge Cases

External code can technically access private fields and bypass validation. A stale `struct xe_guc_buf` after release can become a use-after-free if reused.

## Test Signals

Tests should focus on API-level behavior rather than direct field access: valid/invalid checks, lifetime, and suballocation manager capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_buf_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_capture.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_capture.c

## Purpose

`xe_guc_capture.c` defines GuC error-capture register lists, registers those lists for ADS consumption, processes GuC state-capture log output after engine resets, supports manual engine capture, matches captured nodes to timed-out exec queues, and prints captured engine register state for devcoredump/debug output.

## Important APIs, Types, and Functions

- Public list APIs: `xe_guc_capture_getlistsize()`, `xe_guc_capture_getlist()`, `xe_guc_capture_getnullheader()`, `xe_guc_capture_ads_input_worst_size()`, and `xe_guc_capture_get_reg_desc_list()`.
- Runtime processing: `xe_guc_capture_process()` reads GuC log capture output and turns it into parsed nodes on `outlist`.
- Snapshot integration: `xe_guc_capture_get_matching_and_lock()`, `xe_engine_manual_capture()`, `xe_engine_snapshot_capture_for_queue()`, `xe_engine_snapshot_print()`, and `xe_guc_capture_put_matched_nodes()`.
- Init: `xe_guc_capture_init()` selects platform static register lists and initializes lists; `xe_guc_capture_steered_list_init()` creates dynamic steered register descriptors and preallocated output nodes.
- Internal state includes `struct xe_guc_state_capture`, `__guc_capture_parsed_output`, ADS list caches, dynamic extension lists, and cache/out linked lists.

## Control Flow

At init, the file selects register descriptor tables by graphics version. ADS population asks for sizes and cached list blobs; after hwconfig, steered render/compute registers are expanded per DSS steering target. Runtime GuC capture notifications cause the driver to copy log-buffer state, detect overflow, parse group headers and capture headers from the circular state-capture region, allocate or recycle preallocated parsed nodes, attach global/class/instance register lists, and add nodes to `outlist`. Later devcoredump code matches nodes by GuC class, instance, GuC id, and LRCA or falls back to manual MMIO capture.

## State and Persistence Behavior

`guc->capture` persists for the GuC lifetime and owns descriptor caches, dynamic extension lists, node cache, and output list. Parsed nodes are recycled between cache and output lists; matched nodes are marked `locked` to prevent stale removal until devcoredump releases them. The GuC log read pointer and flush flags are updated in the log BO after processing.

## Dependencies and Integration Points

It integrates GuC capture/log ABI, ADS registration, GT topology steering, hardware engine definitions, LRC and exec-queue state, GuC submission reset handlers, devcoredump snapshots, MMIO/MCR reads, DRM managed allocations, and GuC CT acknowledgements for log flush completion.

## Risks and Edge Cases

The parser must handle circular buffer wrap, overflow, malformed lengths, partial captures, unknown capture types, and too many registers per node. Linked-list access is not guarded by an obvious lock in this file, so callers rely on higher-level sequencing around capture processing and devcoredump. The print path still dereferences live GT/engine pointers, called out by an in-code FIXME. Dynamic steered-list sizing depends on fuse topology being initialized.

## Test Signals

Tests should exercise platform list selection, size caching, steered list generation from DSS masks, circular log parsing with wrap/overflow/malformed entries, node recycling and stale-match removal, manual capture on render/compute and non-render classes, 64-bit register print ordering warnings, and matching by GuC id/LRCA. Integration signals include devcoredump output containing GuC or manual capture data after resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_capture.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_capture.h

## Purpose

`xe_guc_capture.h` declares the GuC capture API and maps Xe/GuC engine classes into GuC capture-list classes.

## Important APIs, Types, and Functions

- `xe_guc_class_to_capture_class()` maps GuC render and compute to render/compute capture, GSC other to GSC, and video/blitter classes directly.
- `xe_engine_class_to_guc_capture_class()` composes Xe engine class to GuC class and then to capture class.
- Public functions cover capture processing, ADS list retrieval and sizing, null list retrieval, worst-case ADS sizing, descriptor list lookup, matching/locking output nodes, manual capture, snapshot printing/capture, steered-list initialization, matched-node cleanup, and capture init.

## Control Flow

GuC init calls capture init, ADS calls list sizing/retrieval, CT event handling calls `xe_guc_capture_process()`, and devcoredump/snapshot paths call matching, manual capture, printing, and cleanup helpers.

## State and Persistence Behavior

The header exposes opaque parsed-output pointers and operates on `struct xe_guc`, `struct xe_exec_queue`, and hardware engine snapshots. Actual state lives in `guc->capture`.

## Dependencies and Integration Points

It includes GuC capture/scheduler ABI and `xe_guc.h`, so it connects firmware class constants, Xe engine classes, ADS, CT event handling, and devcoredump reporting.

## Risks and Edge Cases

Invalid engine classes warn and return `GUC_CAPTURE_LIST_CLASS_MAX`; callers must not use that as a real class. The API exposes internal parsed-output pointers, making lifetime rules important for callers that lock and later release matched nodes.

## Test Signals

Tests should verify class mapping, invalid-class handling, ADS list calls for every owner/type/class combination, and matched-node lock/release lifetimes through devcoredump flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_capture.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_capture_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_capture_types.h

## Purpose

`xe_guc_capture_types.h` defines register descriptor types used by GuC capture list generation and reporting.

## Important APIs, Types, and Functions

- `enum capture_register_data_type` distinguishes 32-bit registers, low dword of a 64-bit register, and high dword of a 64-bit register.
- `struct __guc_mmio_reg_descr` describes one register: offset, data type, GuC flags, mask, cached DSS id for steered registers, and printable name.
- `struct __guc_mmio_reg_descr_group` groups descriptor arrays by owner, capture type, and engine class.

## Control Flow

Static descriptor tables and dynamic steered lists use these types to build GuC ADS capture lists. Runtime printing uses the descriptors to format captured values in descriptor order and combine adjacent 64-bit low/high pairs.

## State and Persistence Behavior

Descriptors are mostly static const tables; dynamic extension descriptors are DRM-managed allocations built after topology is known. Captured runtime values are stored separately in GuC ABI `struct guc_mmio_reg` arrays.

## Dependencies and Integration Points

The header depends on `regs/xe_reg_defs.h` and Linux types. It is used by capture implementation, ADS capture-list registration, and snapshot printing.

## Risks and Edge Cases

64-bit registers require correct consecutive low/high descriptor ordering; print code warns on invalid order. Steered descriptors need accurate flags, group, instance, and DSS id or dumps will be misleading. Names can be NULL for low halves and must be handled by printers.

## Test Signals

Descriptor validation should check 64-bit pair ordering, non-null names where printed, class/type owner consistency, and steered flag/group/instance encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_capture_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ct.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ct.c

## Purpose

`xe_guc_ct.c` implements the GuC Command Transport layer: bidirectional circular CT buffers, CTB registration, H2G send paths, blocking send/receive fences, G2H event parsing/dispatch, flow-control credit accounting, safe-mode polling, fast IRQ handling for critical messages, runtime state transitions, snapshots, and debug dead-CT capture.

## Important APIs, Types, and Functions

- Init/lifecycle: `xe_guc_ct_init_noalloc()`, `xe_guc_ct_init()`, `xe_guc_ct_init_post_hwconfig()`, `xe_guc_ct_enable()`, `xe_guc_ct_restart()`, `xe_guc_ct_disable()`, `xe_guc_ct_stop()`, runtime suspend/resume, and flush/stop.
- Sends: `xe_guc_ct_send()`, `xe_guc_ct_send_locked()`, `xe_guc_ct_send_g2h_handler()`, `xe_guc_ct_send_recv()`, and `xe_guc_ct_send_recv_no_fail()`.
- Receive/dispatch: `xe_guc_ct_fast_path()`, `receive_g2h()`, `dequeue_one_g2h()`, `parse_g2h_msg()`, `process_g2h_msg()`, and action-specific handler calls.
- Diagnostics: `xe_guc_ct_snapshot_capture()`, `xe_guc_ct_snapshot_print()`, `xe_guc_ct_snapshot_free()`, `xe_guc_ct_print()`, and debug-only `ct_dead_*` capture.

## Control Flow

Noalloc init sets locks, xarray, waitqueues, and workers. Alloc init creates pinned mapped H2G/G2H BOs. Enabling zeroes CTBs, initializes descriptors, self-configures descriptor/buffer addresses and sizes through MMIO, sends CT enable, marks state enabled, wakes waiters, and starts safe-mode polling when MSI is absent. H2G send reserves H2G and optional G2H credits, writes CT and HXG headers plus payload into the circular buffer, updates tail, and rings GuC. Blocking send stores a stack fence in an xarray by sequence number and waits for a matching G2H response. IRQ/workqueue receive reads complete G2H messages, validates origin/type, releases credits, wakes fences, and dispatches events to submission, page fault, TLB invalidation, page reclaim, relay, SR-IOV, capture, crash, and test handlers.

## State and Persistence Behavior

Persistent CT state includes two CTBs, a mutex for send/dequeue serialization, a fast spinlock for G2H credits and IRQ fast path, fence sequence/xarray, outstanding G2H credit count, waitqueues, workers, and state enum. State transitions cancel all in-flight fences and reset credit accounting. Debug builds also maintain dead-CT snapshots and a ring of fast-request fence origins.

## Dependencies and Integration Points

The CT layer integrates GuC ABI headers, BO mapping, MMIO self-config through `xe_guc_self_cfg*`, runtime PM, GT reset, submission, pagefault/TLB/page-reclaim handlers, relay, SR-IOV PF monitor/control, GuC log/capture, tracepoints, fault injection, and devcoredump snapshot printing.

## Risks and Edge Cases

Credit accounting must stay exact or CT deadlocks. H2G wrap writes NOPs and retries, which depends on space recalculation. Blocking sends use stack fences and require xarray erase plus mutex serialization to avoid UAF after timeout. Fast-request failures cannot be returned to senders and escalate to reset. Safe-mode polling must not race with normal IRQ handling. Runtime PM receive paths intentionally avoid waking a suspended device, so unsolicited events around suspend may be dropped.

## Test Signals

Tests should cover CTB init/register, H2G wrap, H2G/G2H room accounting, blocking response success/failure/retry/timeout/cancel, state transitions canceling fences, invalid descriptor status/head/tail handling, fast-path pagefault/TLB/page-reclaim dispatch, safe-mode polling, runtime suspend/resume invariants, snapshot printing, and debug dead-CT capture. Fault injection hooks cover init and send/receive functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ct.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ct.h

## Purpose

`xe_guc_ct.h` declares the public Command Transport API and small inline helpers for CT state and IRQ handling.

## Important APIs, Types, and Functions

It exposes CT init, post-hwconfig, enable/restart/disable/stop, runtime suspend/resume, send/send-recv variants, G2H-handler send, no-fail send-recv, queue processing time, snapshot capture/print/free, and immediate print. Inline helpers include `xe_guc_ct_initialized()`, `xe_guc_ct_enabled()`, `xe_guc_ct_irq_handler()`, `xe_guc_ct_send_block()`, `xe_guc_ct_send_block_no_fail()`, and `xe_guc_ct_wake_waiters()`.

## Control Flow

The IRQ helper checks that CT is enabled, wakes CT waiters, queues the G2H worker, and invokes the fast path. Send APIs are split between nonblocking events, blocking request/response, locked callers, and G2H-handler contexts.

## State and Persistence Behavior

State is stored in `struct xe_guc_ct` from `xe_guc_ct_types.h`. The inline enabled/initialized checks use `READ_ONCE()` paired with implementation `WRITE_ONCE()`.

## Dependencies and Integration Points

It includes CT types and forward-declares DRM/device objects. It is included by GuC lifecycle, ADS, capture, submission, TLB, reset, and IRQ code.

## Risks and Edge Cases

`xe_guc_ct_irq_handler()` must only be called with an initialized CT and a valid workqueue. Locked send APIs require the caller to already hold the CT mutex where documented by implementation. No-fail send is intended for reset-in-progress paths, not arbitrary commands.

## Test Signals

Compile tests catch prototype drift. Runtime tests should verify IRQ helper behavior when disabled/enabled, send-block wrappers, and state helper consistency across transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ct_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ct_types.h

## Purpose

`xe_guc_ct_types.h` defines the persistent data structures for the GuC CT layer, including CTB descriptors, snapshots, state enum, debug dead-CT state, fast-request tracking, and the main `struct xe_guc_ct`.

## Important APIs, Types, and Functions

- `struct guc_ctb_info` caches CTB size, reserved space, head, tail, free space, and broken status.
- `struct guc_ctb` pairs a BO with descriptor and command maps plus cached info.
- `struct guc_ctb_snapshot` and `struct xe_guc_ct_snapshot` capture descriptor/info and optional raw CTB bytes for later printing.
- `enum xe_guc_ct_state` defines not-initialized, disabled, stopped, and enabled states.
- Debug-only `struct xe_dead_ct` stores dead-channel reason, snapshots, and worker.
- Debug-only `struct xe_fast_req_fence` records recent fast-request fences/actions and optional call stacks.
- `struct xe_guc_ct` owns locks, H2G/G2H CTBs, outstanding G2H count, workers, state, fence sequence/xarray, waitqueues, message buffers, and debug state.

## Control Flow

The implementation initializes this structure in stages: lock/workqueue/xarray setup first, BO allocation second, CTB descriptor setup when enabling, and state transitions throughout reset/power operations. Send and receive paths update `guc_ctb_info` under the mutex and fast spinlock.

## State and Persistence Behavior

All fields persist for the GuC/GT lifetime. `g2h_outstanding`, CTB `space/head/tail`, `state`, and `fence_lookup` are highly mutable runtime state. Snapshots are separately allocated copies and must be freed by callers.

## Dependencies and Integration Points

The type depends on interrupt/workqueue, iosys-map, spinlock, waitqueue, xarray, optional stack depot, and GuC CTB ABI structures. It is embedded in `struct xe_guc` and consumed by CT, GuC lifecycle, IRQ, debug, and devcoredump code.

## Risks and Edge Cases

The state structure mixes mutex-protected, spinlock-protected, workqueue, and debug fields; misuse of locking can corrupt credits or fence lookup. `msg` and `fast_msg` are fixed-size protocol buffers and rely on CTB max-length validation. Debug-only fields must not leak assumptions into non-debug builds.

## Test Signals

Tests should validate initial state, CTB info invariants, snapshot allocation/free, xarray fence lifetime under cancellation, debug fast-request wrap behavior, and state transitions preserving lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ct_types.h -->
