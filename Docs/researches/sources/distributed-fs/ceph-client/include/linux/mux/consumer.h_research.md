# sources/distributed-fs/ceph-client/include/linux/mux/consumer.h

Purpose: declares the consumer-side multiplexer API for drivers that need to acquire a mux control or named mux state, select it, optionally delay after switching, try-select without blocking, and deselect it.

Important APIs and types: opaque `struct mux_control` and `struct mux_state` are manipulated through `mux_control_states()`, `mux_control_select_delay()`, `mux_state_select_delay()`, try-select variants, inline zero-delay wrappers, `mux_control_deselect()`, `mux_state_deselect()`, `mux_control_get()`, optional get, put, and device-managed get helpers including preselected state variants. When `CONFIG_MULTIPLEXER` is disabled, required gets return `ERR_PTR(-EOPNOTSUPP)`, optional gets return `NULL`, and operations return `-EOPNOTSUPP`.

Control flow: a consumer obtains a mux control or state from device resources, selects the desired state before accessing the downstream resource, optionally observes a settle delay, performs its operation, then deselects or lets devm cleanup release resources. Try-select paths let consumers avoid sleeping or avoid contended selection.

State and persistence: consumer-visible state is the selected mux state held in the mux core and hardware. The header itself stores none; devm helpers bind lifetime to the requesting device.

Dependencies and integration points: depends on the multiplexer core and device model. It integrates I2C/SPI/regulator/PHY-style consumers with mux providers through firmware-described or platform-described mux resources.

Risks and test signals: risks include ignoring `ERR_PTR` versus optional `NULL`, forgetting deselect on error paths, assuming disabled-config stubs succeed, using state counts without validating indices, and missing hardware settle delays. Test enabled and disabled `CONFIG_MULTIPLEXER`, optional resource absence, contended try-select, devm cleanup, preselected state helpers, and error unwinding that must deselect.
