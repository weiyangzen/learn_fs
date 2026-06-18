# sources/distributed-fs/ceph-client/drivers/iio/industrialio-backend.c

## Purpose
`industrialio-backend.c` implements the IIO backend framework used by aggregate converter devices where a frontend IIO device, such as an ADC or DAC driver, delegates low-level digital-interface, DMA, timing, formatting, or calibration operations to one or more backend devices. Backends register themselves globally, frontends resolve them through firmware-node references, and the framework supplies exported wrappers around `struct iio_backend_ops` with argument validation, lifetime management, debugfs integration, and devm cleanup.

## Important APIs, types, and functions
- `struct iio_backend` is the private framework object. It stores the backend ops, backend device, consumer/frontend device, provider module owner, private driver data, firmware-visible name, cached debugfs register address, capability bits, list node, and frontend-relative index.
- `struct iio_backend_buffer_pair` binds a backend and requested `struct iio_buffer` for devm cleanup.
- `iio_backend_op_call()`, `iio_backend_ptr_op_call()`, and `iio_backend_void_op_call()` are internal dispatch macros that return `-EOPNOTSUPP` when an operation is absent.
- Exported operation wrappers include channel enable/disable, backend enable/disable, data format/source/sample-rate/test-pattern/status, I/O delay, sample trigger, raw reads, interface type, data size, oversampling, filter type, data alignment, lane count, DDR mode, stream enable, data-transfer address, and capability checks.
- `iio_backend_extend_chan_spec()` lets a backend add channel ext_info while enforcing that backend ext_info callbacks use `iio_backend_ext_info_get()` and `iio_backend_ext_info_set()`.
- `devm_iio_backend_request_buffer()` requests a backend-owned buffer and registers a devm action that calls backend `free_buffer`.
- `devm_iio_backend_get()`, `devm_iio_backend_fwnode_get()`, and `__devm_iio_backend_get_from_fwnode_lookup()` resolve registered backends by `io-backends` firmware references or legacy fwnode lookup.
- `devm_iio_backend_register()` allocates the private backend object, records metadata from `struct iio_backend_info`, inserts it into `iio_back_list`, and removes it through a devm action.
- `iio_backend_debugfs_add()` creates per-backend `backendN` debugfs directories under the frontend IIO debugfs node.

## Control flow
Backend providers call `devm_iio_backend_register()` during probe. The backend object is devm-allocated, populated from `iio_backend_info`, and inserted into the global `iio_back_list` under `iio_back_lock`. Consumers call `devm_iio_backend_get()` or a fwnode variant. The resolver finds the requested `io-backends` reference, walks the backend list, obtains a provider module reference with `try_module_get()`, registers a devm release action, creates a supplier/consumer device link, records `frontend_dev`, and returns the backend pointer. If no matching provider exists yet, the fwnode path returns `-EPROBE_DEFER`.

Runtime frontend calls go through small wrappers that validate enumerated inputs and then call the backend operation. Ext-info callbacks are a special case: because sysfs callbacks receive only the frontend `iio_dev`, `iio_backend_ext_info_get()` and `_set()` infer the backend from the frontend parent. That inference deliberately rejects multiple matching backends, requiring such frontends to provide more explicit routing.

Debugfs access is optional. If the frontend IIO debugfs directory exists and the backend supplies either register access or a name, `iio_backend_debugfs_add()` creates `backendN/direct_reg_access` and/or `backendN/name`. The register file stores a cached address on one-value writes and performs writes on two-value input.

## State and persistence behavior
Framework state is in-memory only: the global backend list, provider module references, device links, `frontend_dev` associations, cached debugfs register address, and backend index. Hardware state changes are delegated to backend ops and may persist according to the backend device. `devm_iio_backend_enable()` and `devm_iio_backend_request_buffer()` bind disable/free operations to consumer-device lifetime. Registration cleanup removes the backend from the global list; consumer cleanup drops the provider module reference via `iio_backend_release()`.

## Dependencies and integration points
The file depends on Linux device links, firmware-node property references (`io-backends` and `io-backend-names`), debugfs, module ownership, devm actions, the IIO core, and `include/linux/iio/backend.h`. It integrates with frontend channel sysfs via ext_info callbacks and with backend-provided buffers through the IIO buffer interface.

## Risks
- `iio_backend_ext_info_get()` and `_set()` infer a backend from `indio_dev->dev.parent`; this is intentionally limited and fails for multi-backend frontends unless they route explicitly elsewhere.
- `__devm_iio_backend_get()` records `back->frontend_dev = dev` in the backend object. A backend consumed by multiple frontends or reused unexpectedly would need careful scrutiny.
- Many wrappers rely on backend implementations to serialize hardware access and validate channel numbers; the framework mostly validates enum ranges and null ops.
- Debugfs register access writes to `cached_reg_addr` without a per-backend lock; concurrent debugfs readers/writers can race on the cached address.
- `iio_backend_extend_chan_spec()` rejects overwritten frontend ext_info and backend custom handlers. That protects callback routing but can surprise backend authors expecting to append or customize.

## Test signals
- Build with `CONFIG_IIO_BACKEND` users and `CONFIG_DEBUG_FS` enabled and disabled.
- Probe tests should cover missing `io-backends`, named backend lookup, `-EPROBE_DEFER`, duplicate or multi-backend frontend cases, and device-link/provider module reference cleanup.
- API tests should verify `-EOPNOTSUPP` for absent ops and `-EINVAL` for invalid enum inputs or zero-only constraints.
- Debugfs tests should validate one-value cached address writes, two-value register writes, readback, and backend index naming for multiple named backends.
- Channel extension tests should confirm backend ext_info must use the framework get/set helpers and cannot replace frontend ext_info.
