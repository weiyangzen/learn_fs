# sources/distributed-fs/ceph-client/include/linux/ptp_mock.h

Purpose: declares a mock PTP Hardware Clock helper for virtual network devices and tests that need a PHC index without real hardware.

Important APIs and types: opaque `struct mock_phc` is created with `mock_phc_create()`, destroyed with `mock_phc_destroy()`, and queried for its PHC index with `mock_phc_index()`. Disabled builds return `NULL` and `-1`.

Control flow: a virtual driver creates a mock PHC during device setup, exposes or uses its index for timestamping paths, and destroys it during teardown.

State and persistence: mock clock state is runtime-only and tied to the parent device lifetime.

Dependencies and integration points: depends on `CONFIG_PTP_1588_CLOCK_MOCK`, device model, and PTP clock core. Integrates virtual network devices with timestamping tests or features.

Risks and test signals: risks include leaking mock PHCs on device removal, using `-1` indexes when config is disabled, and diverging behavior from real PHCs. Test create/destroy cycles, index visibility, virtual device teardown, and disabled config fallbacks.
