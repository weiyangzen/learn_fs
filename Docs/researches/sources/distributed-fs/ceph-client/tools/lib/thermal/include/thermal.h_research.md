# sources/distributed-fs/ceph-client/tools/lib/thermal/include/thermal.h

Purpose: Public C API for `libthermal`, defining operations callbacks, thermal data structures, iteration helpers, discovery/init/exit, and netlink command/event/sampling functions.

Important APIs/types/functions: Defines callback groups `thermal_sampling_ops`, `thermal_events_ops`, and `thermal_ops`; data structures `thermal_trip`, `thermal_threshold`, `thermal_zone`, and `thermal_cdev`; `thermal_error_t`; callback typedefs for iterators; public functions annotated with `LIBTHERMAL_API`.

Control flow: Consumers provide `thermal_ops` to `thermal_init()`, discover zones with command APIs or `thermal_zone_discover()`, iterate sentinel-terminated arrays with `for_each_*`, handle events/sampling through fds and handle functions, and clean up with `thermal_exit()`.

State and persistence: Data arrays are heap-allocated by command code and sentinel-terminated. `struct thermal_handler` is opaque to public users. No persistence beyond process memory.

Dependencies/integration: Includes Linux thermal UAPI and sys types. Provides C linkage guards for C++ consumers and default visibility attributes for shared library exports.

Risks: The `extern "C"` closing block appears after the `#endif /* __LIBTHERMAL_H */`, so in C++ the closing brace is outside the include guard; repeated includes could be problematic. Ownership/freeing rules for discovered arrays are not documented in the header. Callback pointers may be NULL, but some handlers assume enabled callbacks exist.

Test signals: Compile from C and C++, ABI visibility checks, iterator behavior with NULL and sentinel arrays, and lifecycle tests using `thermal_init()`/`thermal_exit()`.
