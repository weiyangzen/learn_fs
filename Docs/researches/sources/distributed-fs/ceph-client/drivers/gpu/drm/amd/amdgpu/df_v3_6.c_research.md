# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v3_6.c

## Purpose

This file implements Data Fabric 3.6 operations for AMDGPU. In addition to the channel-count and clock-gating helpers seen in earlier DF revisions, it supports DF fabric indirect config access, perfmon counter assignment/start/stop/read flows, a sysfs counter-availability attribute, memory-hash status querying, and RAS poison-mode detection.

## Important APIs and Functions

Fabric indirect config access:

- `df_v3_6_get_fica()` and `df_v3_6_set_fica()` access FICA address/data registers through NBIO-provided PCIe index/data offsets. They serialize the index/data sequence with `adev->reg.pcie.lock`.

Perfmon low/high register access:

- `df_v3_6_perfmon_rreg()` reads paired low/high counter registers atomically under the PCIe register lock.
- `df_v3_6_perfmon_wreg()` writes paired low/high registers atomically.
- `df_v3_6_perfmon_arm_with_status()` writes control registers and verifies readback, returning `-EBUSY` on mismatch.
- `df_v3_6_perfmon_arm_with_retry()` retries arming for up to 1 ms in 100 us intervals and returns `-ETIME` on timeout.

Perfmon allocation and operation:

- Config encoding macros split `config` into event, instance, and unitmask fields.
- `df_v3_6_pmc_add_cntr()` allocates one of four visible counters by filling `adev->df_perfmon_config_assign_mask[]`.
- `df_v3_6_pmc_get_addr()` maps assigned counter indexes 0-3 to SMN perfmon control or counter low/high addresses.
- `df_v3_6_pmc_get_ctrl_settings()` translates config fields into control register values and enable bit state.
- `df_v3_6_pmc_start()` either allocates a counter or arms it for Vega20/Arcturus. Failed arming marks the counter deferred.
- `df_v3_6_pmc_stop()` disables a counter and optionally resets/releases it.
- `df_v3_6_pmc_get_count()` rearms deferred counters when possible, reads the 64-bit count, and suppresses overflow sentinel values.

DF feature helpers:

- `df_v3_6_query_hashes()` populates `adev->df.hash_status` for specific Arcturus/Aldebaran interleave encodings.
- `df_v3_6_enable_broadcast_mode()`, `df_v3_6_get_fb_channel_number()`, `df_v3_6_get_hbm_channel_number()`, `df_v3_6_update_medium_grain_clock_gating()`, and `df_v3_6_get_clockgating_state()` mirror revision-specific register handling for broadcast mode, interleave/channel decode, and MGCG.
- `df_v3_6_query_ras_poison_mode()` reads hardware assert mask fields and returns true only when all relevant poison-mode fields are set, warning on inconsistent mixed state.
- `df_v3_6_sw_init()` creates `df_cntr_avail`, clears perfmon assignment masks, and queries hash state.
- `df_v3_6_sw_fini()` removes the sysfs file when the device kobject is live.
- `df_v3_6_funcs` exposes all callbacks.

## Control Flow and State

Software initialization creates a read-only sysfs attribute and initializes `adev->df_perfmon_config_assign_mask[]` to zero. Perfmon flows split into allocation and programming: an add call reserves a logical counter, a start call programs control registers, reads later consult the assignment mask, and stop/remove disables and releases the slot. Deferred arming is persisted by OR-ing `DEFERRED_ARM_MASK` into the assignment mask, so `pmc_get_count()` can retry arming later.

Hardware state is primarily DF registers reached through SOC15 and SMN/PCIe index-data access. Software state includes hash-status booleans and the perfmon assignment mask. Locking around PCIe index/data sequences is essential because low/high register access and indirect FICA access must be atomic with respect to other users of the same index/data aperture.

## Dependencies and Integration Points

The file depends on generated DF 3.6 headers, NBIO funcs for PCIe indirect offsets, Linux device sysfs APIs, AMDGPU DF callback dispatch, RAS code that asks about poison mode, and performance-monitoring users that call `pmc_start`, `pmc_stop`, and `pmc_get_count`. It also branches on ASIC type for Vega20, Arcturus, and Aldebaran-specific behavior.

## Risks and Edge Cases

Key risks are races or corruption if index/data access is not serialized, counter leaks if assignment masks are not released, incorrect handling of deferred arms, overflow sentinel misinterpretation, partial poison-mode settings, mismatched channel-number tables, and sysfs creation/removal lifetime issues. Some callbacks silently do nothing for unsupported ASIC types, so callers must tolerate zero counts or no-op behavior.

## Test Signals

Validation should include sysfs `df_cntr_avail` count changes during perfmon allocation/removal, perfmon start/stop/read on Vega20 and Arcturus, deferred-arm retry behavior under simulated busy hardware, overflow sentinel suppression, FICA read/write serialization, hash-status detection on Arcturus/Aldebaran interleave encodings, RAS poison-mode true/false/inconsistent cases, and MGCG state toggling.
