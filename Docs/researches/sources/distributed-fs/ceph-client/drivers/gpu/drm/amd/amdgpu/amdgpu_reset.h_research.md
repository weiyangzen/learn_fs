## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reset.h

Purpose: declares AMDGPU reset contexts, handler/control objects, reset domains, reset source/flag enums, and helper APIs for reset orchestration and reset-domain synchronization.

Important APIs and types: `enum AMDGPU_RESET_FLAGS` records full reset, skip hardware reset, skip coredump, and host FLR bits. `enum AMDGPU_RESET_SRCS` identifies reset trigger sources. `struct amdgpu_reset_context` carries method, requesting device, job, hive, device list, flags, and source. `struct amdgpu_reset_handler` defines prepare/perform/restore hooks plus optional `do_reset`. `struct amdgpu_reset_control` owns reset work, lock, handlers array, active reset method, and handler lookup/async callbacks. `struct amdgpu_reset_domain` owns a refcounted workqueue, type, rwsem, and reset status atomics.

Control flow: callers create domains, get/put references with kref helpers, schedule work on domain workqueues, lock/unlock domain reset windows, and dispatch through reset handlers. The `for_each_handler` macro iterates registered handler slots until NULL. DPC helpers synchronize PCIe DPC state with `adev->no_hw_access`.

State and persistence: all state is runtime-only and held under `amdgpu_device` or reset-domain objects. The rwsem is the central synchronization primitive between reset and hardware access.

Dependencies and integration points: includes `amdgpu.h` for core device types. It is consumed by reset implementation, register access, GPU recovery, ASIC reset modules, and PCIe DPC handling.

Risks: handler arrays are bounded by `AMDGPU_RESET_MAX_HANDLERS`; missing terminators or wrong hook setup can produce unsupported reset or NULL dereferences in implementation code. `amdgpu_reset_pending()` requires the domain sem to be held and asserts that via lockdep.

Test signals: compile coverage for handler signatures, lockdep for reset-domain helpers, reset work scheduling on both single-device and XGMI domains, and DPC paths toggling no-hardware-access state.
