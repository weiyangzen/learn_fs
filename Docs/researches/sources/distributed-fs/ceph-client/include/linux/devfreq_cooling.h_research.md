# sources/distributed-fs/ceph-client/include/linux/devfreq_cooling.h

Purpose: Declares thermal cooling-device registration helpers for devfreq-managed devices.

Important APIs, types, and functions: Defines `struct devfreq_cooling_power` with optional `get_real_power()` and declares `of_devfreq_cooling_register_power()`, `of_devfreq_cooling_register()`, `devfreq_cooling_register()`, `devfreq_cooling_unregister()`, and `devfreq_cooling_em_register()`.

Control flow: A devfreq device registers as a thermal cooling device, optionally with firmware node data or an energy model and real-power callback. Thermal governors then limit devfreq cooling states, using either estimated utilization-scaled power or driver-reported real power. Unregister tears down the thermal cooling device.

State and persistence: Cooling state is held in the thermal/devfreq framework, including power tables and current cooling limits. This header defines no persistent state.

Dependencies and integration points: Depends on devfreq, thermal framework, device tree nodes, and optionally energy model data. Disabled builds return `ERR_PTR(-EINVAL)` and no-op unregister.

Risks and test signals: Risks include power callbacks exceeding table maximums, stale cooling devices after devfreq removal, wrong OPP/thermal mapping, and missing disabled-config handling. Test thermal zone binding, cooling state changes, EM registration, real-power callbacks, unregister on driver removal, and `CONFIG_DEVFREQ_THERMAL=n`.
