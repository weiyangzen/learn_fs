# `sources/distributed-fs/ceph-client/include/linux/iio/backend.h`

Purpose: frontend/backend abstraction for IIO converter stacks, allowing frontend devices to configure data format, source, sampling, buffers, test patterns, interface timing, filters, debugfs, and backend capabilities.

Important APIs/types/functions: data type/source/sample-trigger/interface/filter enums, capability bits, `IIO_BACKEND_EX_INFO`, `struct iio_backend_data_fmt`, `struct iio_backend_ops`, `struct iio_backend_info`, wrapper APIs for channel enable/disable, backend enable/disable, data format/source, sampling frequency, test pattern, status, I/O delay, buffer request, filter, interface alignment, lanes, DDR, stream, transfer address, ext-info, raw read, channel spec extension, capability checks, priv lookup, devm get/register, and debugfs helpers.

Control flow and state: frontends obtain a backend by firmware/device lookup, check capabilities, then call wrappers that dispatch to backend ops. Persistent backend state and private data live in the implementation registered through `devm_iio_backend_register`.

Dependencies/integration: depends on IIO core, firmware nodes, device-managed resources, and optional debugfs. Common in split ADC/DAC designs where digital backend and analog frontend are separate devices.

Risks: capability bits must match implemented ops; optional ops need clear error returns; enable/disable and stream/DDRadjustment ordering is hardware-sensitive; ext-info private values are uintptr_t; debugfs exposure must not bypass locking.

Test signals: frontend probe with named/fwnode backend, missing op/capability errors, full enable/configure/stream/disable sequence, buffer request/free, channel spec extension, ext-info read/write, debugfs status/reg access, and devm cleanup.
