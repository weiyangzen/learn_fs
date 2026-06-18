## sources/distributed-fs/ceph-client/rust/kernel/regulator.rs

Purpose: wraps Linux regulator consumer APIs for Rust drivers, modeling regulator handles as typestates so enable-reference ownership is reflected by `Regulator<Enabled>` versus `Regulator<Disabled>`.

Important APIs/types/functions: `RegulatorState` is sealed and defines `DISABLE_ON_DROP`; `Enabled` owns an enable refcount, while `Disabled` owns only a regulator reference. `devm_enable` and `devm_enable_optional` provide device-managed one-shot enable helpers. `Regulator<T>` supports `set_voltage`, `get_voltage`, `get_internal`, and internal enable/disable calls. State transitions are `Regulator<Disabled>::try_into_enabled` and `Regulator<Enabled>::try_into_disabled`; failures return `Error<State>` with the original handle for retry. `Voltage` is a transparent microvolt wrapper.

Control flow: acquisition calls `regulator_get`; `Regulator<Enabled>::get` chains disabled acquisition and enable transition. Transitions wrap `self` in `ManuallyDrop` so the old handle is not prematurely dropped while the new typestate is constructed. `Drop` conditionally calls `regulator_disable` based on typestate, then always calls `regulator_put`.

State/persistence: state is a raw `struct regulator *` plus typestate marker. The backing regulator framework maintains global regulator state, enable counts, and voltage configuration; this wrapper persists no state beyond the handle lifetime.

Dependencies/integration: integrates with `Device`, `CStr`, `from_err_ptr`, `to_result`, and C `include/linux/regulator/consumer.h` bindings. Device-managed helpers integrate with devres-managed teardown.

Risks: incorrect typestate conversion would leak or double-release enable counts; `ManuallyDrop` is central to avoiding this. `is_enabled` is implemented only for the sealed `IsEnabled` trait currently implemented for `Disabled`, matching the notion that disabled handles may query actual hardware state. Drop ignores `regulator_disable` errors, as destructors cannot report failure.

Test signals: no local KUnit tests. Doctests document acquisition, voltage set/get, state transitions, retry-on-error, and devm helpers. Runtime validation should use driver probe/remove tests checking enable counts, optional regulator absence, and voltage error paths.
