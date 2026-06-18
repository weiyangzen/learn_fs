# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gfx.h

## Purpose
`amdgpu_gfx.h` is the common graphics/compute IP state and API contract for AMDGPU. It defines queue limits, compute partition modes, RAS memory identifiers, ME/MEC/KIQ structures, graphics configuration caches, CU layout, cleaner shader/isolation state, `struct amdgpu_gfx`, ASIC function tables, and prototypes implemented by `amdgpu_gfx.c`.

## Important APIs, types, and functions
Important types include `struct amdgpu_gfx`, `struct amdgpu_gfx_funcs`, `struct kiq_pm4_funcs`, `struct amdgpu_kiq`, `struct amdgpu_mec`, `struct amdgpu_me`, `struct amdgpu_gfx_config`, `struct amdgpu_cu_info`, `struct amdgpu_gfx_ras`, `struct amdgpu_gfx_shadow_info`, and `struct amdgpu_isolation_work`. Enums define graphics pipe priorities, XCP compute partition modes, partition memory allocation modes, queue unmap actions, and GFX RAS memory IDs. Inline helpers convert partition modes to sysfs text and create bitmasks.

## Control flow
The header has no standalone execution, but it defines how GC implementations plug into common code. ASIC files fill `amdgpu_gfx_funcs` for register selection, wave reads, partition queries/switching, XCC mapping, and HDP flush-mask lookup. KIQ packet emitters are provided through `kiq_pm4_funcs`, and common code calls those function pointers while mapping queues, invalidating TLBs, querying status, or resetting hardware queues.

## State and persistence behavior
`struct amdgpu_gfx` aggregates volatile driver state for firmware handles and versions, rings, queue counts, queue bitmaps, IRQ sources, CU/config caches, power-gating state, RAS pointers, XCC partition state, MQD backup buffers, cleaner shader BO state, delayed isolation work, workload profile counters, and debug/control flags. The state is not durable across driver reloads; it mirrors firmware images, hardware topology, and runtime submissions.

## Dependencies and integration points
The header depends on ring, RLC, IMU, SOC15, RAS, ring mux, and XCP declarations. It is included by common GFX code and generation-specific GC implementations, and it exposes the common API used by scheduler, VM/TLB, RAS, KFD, PM, sysfs, and debugfs code.

## Risks and edge cases
Because this header defines shared layout, changes can affect many IP-version implementations. Queue limit constants must remain consistent with ring arrays and KIQ queue masks. Function pointer contracts need null checks in users. `amdgpu_gfx_create_bitmask()` shifts a 64-bit one and returns `u32`, so callers must not request unsupported widths. The structure carries many per-XCC arrays; incorrect indexing by logical XCC/XCP can corrupt state for partitioned devices.

## Test signals
Build coverage across multiple ASIC generations, queue map/unmap tests, XCP partition tests, cleaner shader tests, RAS query/injection paths, KIQ TLB invalidation, and debugfs/sysfs interface tests are the main validation signals for this header contract.
