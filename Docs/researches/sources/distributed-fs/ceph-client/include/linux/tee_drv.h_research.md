<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tee_drv.h -->
# sources/distributed-fs/ceph-client/include/linux/tee_drv.h

## Purpose
declares the public kernel client-driver API for interacting with TEE devices and trusted applications.

## Important APIs, Types, and Functions
The file is 338 lines and exports these visible symbol families: types/enums `tee_device`, `tee_context`, `tee_shm`, `tee_param_memref`, `tee_param_ubuf`, `tee_param_objref`, `tee_param_value`, `tee_param`, `tee_client_device`, `tee_client_driver`; macros/constants none; function-like macros `to_tee_client_device`, `to_tee_client_driver`, `tee_client_driver_register`, `module_tee_client_driver`; inline helpers `tee_shm_get_size`, `tee_shm_get_page_offset`; external prototypes `tee_shm_alloc_kernel_buf`, `tee_shm_register_kernel_buf`, `tee_shm_register_fd`, `tee_shm_free`, `tee_shm_get_va`, `tee_shm_get_pa`, `tee_client_open_context`, `tee_client_close_context`, `tee_client_get_version`, `tee_client_open_session`, `tee_client_close_session`, `tee_client_system_session`, `tee_client_invoke_func`, `tee_client_cancel_req`, and 2 more.

## Control Flow
Kernel clients open a context with `tee_client_open_context()`, allocate or register shared memory, open a TA session, invoke functions with `tee_param` arrays, optionally cancel requests, close sessions, free memory, and close the context. TEE bus drivers bind through `tee_client_driver` and module helper macros.

## State and Persistence Behavior
`tee_context` tracks the selected device, driver-private data, refcount, release state, supplicant wait policy, and NULL memref capability. `tee_shm` tracks backing pages/addressing, object ID, secure-world ID, flags, and reference count. Parameters carry memrefs, user buffers, object refs, or value triples.

## Dependencies and Integration Points
It depends on the device model, kref, module device IDs, TEE UAPI definitions, and the TEE core's private types. It integrates with in-kernel OP-TEE consumers such as RPMB, firmware, trusted keys, and service devices. Direct includes are `linux/device.h`, `linux/kref.h`, `linux/list.h`, `linux/mod_devicetable.h`, `linux/tee.h`, `linux/types.h`.

## Risks and Edge Cases
Shared-memory offsets and sizes must be bounds-checked before passing to secure world. Context refcycles during release are explicitly called out; supplicant blocking policy matters for non-blocking kernel clients. Session return codes and Linux errno are separate channels.

## Test Signals
Exercise client open/match/close, kernel-buffer allocation and fd registration, VA/PA/page accessors with bounds failures, TA session lifecycle, cancellation, tee bus probe/remove/shutdown, and refcount leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tee_drv.h -->
