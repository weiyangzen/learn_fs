# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_df.h

## Purpose

`amdgpu_df.h` declares the AMDGPU Data Fabric abstraction. It is a compact header that stores Data Fabric hash capability state and a per-ASIC function table used by the rest of the driver to initialize DF support, query channel topology, control DF broadcast/clock-gating/ECC behavior, access DF performance counters, access FICA registers, and query RAS poison mode.

The header intentionally contains no implementation logic. It defines the contract that DF implementation files fill in and that callers access through `adev->df.funcs`.

## Important Types and APIs

- `struct amdgpu_df_hash_status` records whether Data Fabric address hashing is enabled/supported for `64k`, `2m`, and `1g` granularities. This state is stored under `struct amdgpu_df` and can be consumed by memory-management and topology paths that need to understand address distribution.
- `struct amdgpu_df_funcs` is the function-table contract for a DF implementation:
  - `sw_init()` / `sw_fini()` initialize and tear down software DF state.
  - `hw_init()` performs hardware initialization.
  - `enable_broadcast_mode()` toggles broadcast access across DF instances.
  - `get_fb_channel_number()` and `get_hbm_channel_number()` report framebuffer/HBM channel topology.
  - `update_medium_grain_clock_gating()` and `get_clockgating_state()` control/report DF clock-gating state.
  - `enable_ecc_force_par_wr_rmw()` toggles ECC forced partial-write read-modify-write handling.
  - `pmc_start()`, `pmc_stop()`, and `pmc_get_count()` expose DF performance monitor counter operations by config and counter index.
  - `get_fica()` and `set_fica()` abstract FICA register access using FICAA/FICADL/FICADH values.
  - `query_ras_poison_mode()` reports whether DF/RAS poison mode is active/supported for the device.
- `struct amdgpu_df` embeds the current `hash_status` and a `const struct amdgpu_df_funcs *funcs` pointer selected by ASIC/IP discovery code.

## Control Flow and State

DF control flow is indirect. During device/IP setup, ASIC-specific code assigns `adev->df.funcs` and may call `sw_init()`/`hw_init()` through the AMDGPU IP block lifecycle. Later call sites guard on the presence of `adev->df.funcs` and individual callbacks, then invoke the relevant function for clock gating, RAS, performance counters, topology queries, or register access.

Persistent state in this header is limited to `amdgpu_df_hash_status` and the immutable function-table pointer. Counter state, register side effects, and hardware programming are implementation-specific and not stored in this header. Because the function table is `const`, runtime mutation should occur in implementation-private state or `adev->df.hash_status`, not by editing callback slots.

## Dependencies and Integration Points

The declarations depend on `struct amdgpu_device` being visible to users of the header, so it is designed for inclusion from AMDGPU internal code rather than standalone compilation. The callbacks integrate with device initialization, power management, clock gating, RAS poison handling, memory-channel topology, and performance monitoring. The FICA callbacks expose low-level DF register access through a uniform interface so ASIC generation differences can stay in the implementation files.

## Risks and Edge Cases

- Callers must treat every callback as optional unless the selected ASIC generation guarantees it. A missing `funcs` pointer or missing callback should not be dereferenced.
- PMC operations take a raw `config`, `counter_idx`, and add/remove flags; mismatched start/stop/remove semantics can leak counters or return misleading counts.
- Broadcast-mode and FICA operations can affect multiple DF instances or low-level fabric registers, so callers need serialization and ASIC-specific preconditions from the implementation.
- Hash-status booleans are compact but easy to misinterpret: they describe address hash modes, not memory page-size support in general.
- RAS poison-mode reporting is function-table based, so devices without a callback need a conservative fallback in callers.

## Test and Validation Signals

- Build tests should cover all DF implementation files that instantiate `struct amdgpu_df_funcs`, ensuring callback signatures match this header.
- Device init tests should verify `adev->df.funcs` is assigned for supported ASICs and absent or safely ignored for unsupported ones.
- Clock-gating tests should confirm `update_medium_grain_clock_gating()` and `get_clockgating_state()` agree with PM flags after gate/ungate cycles.
- PMC tests should cover start, read, stop, add/remove variants, invalid counter indices, and multiple counter configurations.
- RAS tests should verify poison-mode query behavior with and without callback support.
- FICA tests should validate read/write paths on each supported DF generation and confirm broadcast mode is disabled or enabled only when expected.
