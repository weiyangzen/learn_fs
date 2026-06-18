# sources/distributed-fs/ceph-client/rust/kernel/opp.rs

## Purpose
Wraps the Linux OPP subsystem for Rust drivers. It models dynamic operating performance points, device OPP configuration, OPP table lookup and mutation, optional cpufreq table generation, energy-model registration, and refcounted OPP handles.

## APIs, Types, and Functions
Unit wrappers `MicroVolt` and `MicroWatt` convert to `c_ulong`; `Data` builds `dev_pm_opp_data` for dynamic entries; `Token` removes a dynamic OPP on drop. `SearchType` selects exact, floor, or ceil lookup. `ConfigOps` exposes optional clock and regulator callbacks through a vtable-style trait, and `Config<T>` accumulates property names, clock names, regulator names, supported hardware, and required-device settings before `set` returns a `ConfigToken`. `Table` wraps `opp_table` and exposes `from_dev`, OF constructors, count/latency/suspend queries, sharing CPU helpers, voltage adjustment, rate and OPP setting, frequency/level/bandwidth lookup, enable/disable, cpufreq table creation, and energy-model registration. `OPP` wraps `dev_pm_opp` and exposes frequency, voltage, level, power, required pstate, and turbo state.

## Control Flow, State, and Persistence
Most operations are thin checked calls into `dev_pm_opp_*`. RAII drives persistence: `Token::drop` removes dynamic OPPs, `ConfigToken::drop` clears OPP config, `Table::drop` releases the table reference and conditionally unregisters EM or removes OF/cpumask tables, `FreqTable::drop` frees cpufreq tables, and `ARef<OPP>` releases OPP refs through `AlwaysRefCounted`. `Config::set` builds temporary null-terminated pointer arrays from owned `CString`s and relies on the OPP core not retaining those arrays after the call. C callbacks recover `Device`, `Table`, and `OPP` references and translate Rust `Result` to errno.

## Dependencies and Integration
Depends on `Device`, `ARef`, `Cpumask`, `CpumaskVar`, `Hertz`, `CString`, `KVec`, generated OPP/cpufreq/regulator bindings, `CONFIG_OF`, `CONFIG_CPU_FREQ`, and `CONFIG_ENERGY_MODEL`. Integration points are power management, cpufreq, regulator/clock callbacks, device tree OPP tables, and the energy model.

## Risks and Test Signals
Risks include wrong lifetime assumptions for config pointer arrays, double-removal or missing removal of OF/cpumask tables, lookup APIs returning owned refs with mismatched refcount expectations, exact frequency lookup requiring an `available` value, and callback default vtable methods being used unintentionally. Test signals include dynamic add/drop tests, config-token cleanup tests, OF table add/remove tests under `CONFIG_OF`, refcount leak checks, mocked callback error propagation, and cpufreq/EM cleanup under feature-gated builds.
