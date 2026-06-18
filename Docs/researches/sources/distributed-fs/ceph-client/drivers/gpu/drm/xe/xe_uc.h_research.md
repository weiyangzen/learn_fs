# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc.h

Purpose: Declares the public uC lifecycle interface for Xe GT code.

Important APIs/types/functions: Exposes initialization, post-hwconfig setup, hardware load, reset prepare, runtime suspend/resume, stop prepare/stop/start, suspend prepare/suspend, sanitize reset, and wedge declaration functions for `struct xe_uc`.

Control flow: Device/GT probe and reset paths call init/load/start; suspend/runtime PM paths call suspend/resume helpers; error paths call reset prepare or wedge declaration.

State and persistence behavior: Header has no state; functions mutate the `xe_uc` aggregate declared in `xe_uc_types.h`.

Dependencies and integration points: Forward-declares `struct xe_uc` to keep compile dependencies small. Included by GT lifecycle, reset, PM, and wedge handling code.

Risks: API call order matters. Calling start/stop/load before init or when firmware state is invalid can produce delegated GuC/HuC/GSC errors.

Test signals: Compile coverage and lifecycle integration tests across probe, reset, suspend/resume, and GuC-disabled configurations.
