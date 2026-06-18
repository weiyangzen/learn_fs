# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dev_coredump.h

Purpose: this header defines the amdgpu devcoredump data structures and public lifecycle/API for creating device coredumps after GPU faults.

Important APIs/types: when `CONFIG_DEV_COREDUMP` is enabled, `AMDGPU_COREDUMP_VERSION` identifies the text format. `struct amdgpu_coredump_ring` stores ring read/write pointers, ring index, and snapshot offset. `struct amdgpu_coredump_ib_info` stores an IB GPU address and dword size. `struct amdgpu_coredump_info` stores device pointer, reset task/time, VRAM flags, timed-out ring, ring snapshots, formatted output cache, PASID, IB count, and a counted flexible array of IB descriptors. The header always declares `amdgpu_coredump()`, `amdgpu_coredump_init()`, and `amdgpu_coredump_fini()`.

Control flow and integration: reset and timeout paths call `amdgpu_coredump()` with the affected job and VRAM-loss status. Device init/fini call the lifecycle functions to initialize and flush deferred work. Consumers do not need to know whether the config produces a real coredump or no-op stubs.

State and persistence: the structures describe an in-memory snapshot later exposed by the kernel devcoredump facility. The formatted output is cached to avoid expensive repeated printing during sysfs reads.

Dependencies: the header includes `amdgpu.h`, so it depends on broad driver type definitions. The counted flexible array uses kernel annotations and is only defined under `CONFIG_DEV_COREDUMP`.

Risks: struct layout is part of the private implementation contract between capture, formatting, read, and free functions. Adding fields can increase memory pressure during fault handling. Callers must not dereference config-guarded structs when devcoredump is disabled.

Test signals: config-on/config-off builds, reset path invocation, flexible-array sizing for jobs with multiple IBs, and teardown flushing are the main signals for this interface.
