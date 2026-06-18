# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606_bus_iface.h

Purpose: small platform-data interface for AD7606 parallel/backend bus register access. It gives board/backend glue a way to provide register read/write functions when a parallel interface is paired with an IIO backend.

Important APIs, types, and functions: declares `struct iio_backend` and defines `struct ad7606_platform_data` with `bus_reg_read(struct iio_backend *back, u32 reg, u32 *val)` and `bus_reg_write(struct iio_backend *back, u32 reg, u32 val)`.

Control flow: no executable logic. `ad7606_par.c` fetches `st->dev->platform_data`, calls these callbacks from its `ad7606_bi_bops.reg_read/reg_write`, and returns callback results to the common core.

State and persistence behavior: no state is owned here. The callbacks operate on backend-owned state and volatile ADC registers.

Dependencies and integration points: integrates the AD7606 parallel wrapper with `linux/iio/backend.h` consumers while keeping the header independent via a forward declaration. It is a kernel-internal platform-data contract, not a userspace ABI.

Risks: the parallel wrapper assumes valid platform data when backend register access is used; missing callbacks can cause NULL dereferences if a backend configuration advertises software register access without this data. The interface has no capability discovery or locking, so the common core's direct-mode and mutex rules must be preserved by callers.

Test signals: compile `ad7606_par.c`; probe a backend-backed platform with callback data; exercise debugfs register access and software-mode scale/oversampling writes; test absent or failing backend callbacks in board glue.
