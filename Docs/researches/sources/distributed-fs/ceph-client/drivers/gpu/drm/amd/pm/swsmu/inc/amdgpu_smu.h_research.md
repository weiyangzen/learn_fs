<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/amdgpu_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/amdgpu_smu.h

## Purpose
This header defines the common software SMU contract used by the AMDGPU driver and all ASIC-specific SMU backends. It describes the shared `smu_context`, table/cache abstractions, DPM/user profile state, PMFW message-control structures, feature bitmaps, power policies, thermal and BACO state, the `pptable_funcs` backend vtable, exported SMU helper prototypes, and small inline helpers for cache and feature-list management.

## Important APIs, Types, and Functions
- Core state: `struct smu_context`, `struct smu_table_context`, `struct smu_dpm_context`, `struct smu_power_context`, `struct smu_user_dpm_profile`, `struct smu_feature`, `struct smu_feature_cap`, and `struct stb_context`.
- Table abstractions: `struct smu_table`, `struct smu_table_cache`, `struct smu_driver_table`, `enum smu_table_id`, `enum smu_driver_table_id`, and `SMU_TABLE_INIT`.
- Firmware messaging: `SMU_MSG_MAX_ARGS`, `SMU_MSG_FLAG_*`, `struct smu_msg_config`, `struct smu_msg_args`, `struct smu_msg_ops`, and `struct smu_msg_ctl`.
- Backend callback contract: `struct pptable_funcs` covers firmware loading, table init/transfer, feature control, clocks, display, power limits, fan control, sensors, metrics, power gating, reset, RAS, WBRF, STB, and per-ASIC policy operations.
- Mapping helpers: `MSG_MAP`, `CLK_MAP`, `FEA_MAP`, `TAB_MAP`, `PWR_MAP`, and `WORKLOAD_MAP` map generic SMU IDs to PMFW-specific IDs.
- Inline helpers manage metrics/temp table caches, driver table caches, feature bitmaps/lists, and safe unsigned-16 filtering.

## Control Flow
This file has no standalone execution path, but it shapes the control flow in `amdgpu_smu.c` and backend files. The generic SMU layer stores device state in `struct smu_context`, calls `pptable_funcs` when a concrete ASIC can implement an operation, and uses inline feature/cache helpers to update state without duplicating bitmap or lifetime logic. PMFW messages are described by `smu_msg_args` and are sent through an IP-specific `smu_msg_ops` implementation configured in `smu_msg_ctl`. Table transfers use `smu_table_context` to stage firmware-facing data in BO-backed memory or cached host buffers.

## State and Persistence Behavior
The header defines long-lived state rather than storing it itself. `smu_context` persists for the SMC IP lifetime and contains cached firmware versions, current/default/min/max power limits, OD settings, workload refcounts, user DPM profile, delayed work, WBRF notifier, message lock/control block, and feature bitmaps. Cache validity is time-based: table and driver-table caches require a non-null buffer, nonzero size and interval, a timestamp, and an unexpired jiffies window. Feature lists are bounded by `feature_num` and capped at `SMU_FEATURE_MAX`. Many structures are firmware ABI structures by pointer or table ID, so size, packing, and enum values are persistent cross-component contracts.

## Dependencies and Integration Points
- Includes Linux ACPI WBRF and units headers plus AMDGPU, KGD PP, DC PP, DC SMU, firmware, and SMU type headers.
- Shared by the generic SMU layer, ASIC-specific PPT implementations, display power integration, RAS, debugfs STB code, and firmware message layers.
- The `pptable_funcs` vtable is the key integration boundary between ASIC-independent code and PMFW-specific implementations.
- Table IDs and mappings integrate with PMFW interface headers such as Navi10, Arcturus, Aldebaran, and Cyan Skillfish definitions.

## Risks
- `struct pptable_funcs` is large and partially optional; callers must consistently guard absent callbacks and return the expected errno.
- Firmware ABI structures and mapping macros must stay synchronized with PMFW. Reordering enum values or changing table IDs can silently break mailbox commands or DMA table interpretation.
- Cache helpers rely on correct cache sizes and intervals; stale or undersized cache buffers can leak incorrect metrics.
- Feature helpers limit operations by `feature_num`, so backends with more than the default 64 features need correct initialization.
- `smu_memcpy_trailing` uses compile-time size checks, but both structures must still represent compatible firmware layouts.

## Test Signals
- Compile all SMU backends that include this header to catch callback signature drift and missing type definitions.
- Exercise feature-list conversion to and from arr32 for 64-bit and larger feature sets.
- Validate metrics/temp table caching by forcing cache hit, cache expiry, and size-only temp metrics requests.
- Firmware ABI tests should compare `sizeof` and key offsets for backend PPTable/metrics structures against PMFW expectations.
- Runtime tests should verify all exported prototypes link from AMDGPU, RAS, display, and debugfs users.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/amdgpu_smu.h -->
