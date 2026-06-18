# sources/distributed-fs/ceph-client/drivers/base/test/test_async_driver_probe.c

Purpose: this loadable module tests the device core's asynchronous driver probing behavior by comparing registration latency for async-preferred and forced-synchronous platform drivers.

Important APIs, types, and functions: global atomics track `warnings`, `errors`, `timeout`, and `async_completed`. `test_probe` sleeps for `TEST_PROBE_DELAY`, validates timeout state, and checks NUMA locality for async probes. `async_driver` uses `PROBE_PREFER_ASYNCHRONOUS`; `sync_driver` uses `PROBE_FORCE_SYNCHRONOUS`. `test_platform_device_register_node`, `test_async_probe_init`, and `test_async_probe_exit` manage platform devices and drivers.

Control flow: module init registers one async device per online CPU, times async driver registration, expects it to return faster than half the probe delay, registers a second async device set and again expects fast registration, then registers synchronous devices/driver and expects registration paths to take at least the threshold. It then verifies async probes completed while synchronous work was running. Error paths unregister drivers/devices in reverse order and report accumulated warnings/errors. Module exit unregisters both drivers and fixed-size device arrays.

State and persistence: static arrays store up to `NR_CPUS * 2` async devices and two sync devices. Atomics persist for module lifetime. Platform devices may carry NUMA node information set from CPU topology.

Dependencies and integration points: it integrates with platform bus probing, async probe scheduling, NUMA APIs, CPU iteration, timekeeping, and module init/exit. It is module-only by Kconfig because it performs active timing tests at load time.

Risks: timing thresholds are environment-sensitive; slow systems or heavy load can produce false failures. The init path has a suspicious local use of `cpu_to_node(cpu)` after a `for_each_online_cpu` loop for the first synchronous device, relying on the loop variable value after iteration even though the device is registered with `NUMA_NO_NODE`. Exit loops unregister fixed array sizes and assume NULL-safe platform unregister behavior for entries not created after partial failures.

Test signals: successful module load logs fast async registration, slow sync registration, and "completed successfully". Failures increment atomics and return an error from module init, making the module load fail.
