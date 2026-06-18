<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/clk.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/clk.rs

## Purpose
This file provides Rust abstractions for clock rates and, when `CONFIG_COMMON_CLK` is enabled, reference-counted clock handles.

## Important APIs, Types, and Functions
`Hertz(c_ulong)` represents a frequency and exposes `from_khz`, `from_mhz`, `from_ghz`, `as_hz`, `as_khz`, `as_mhz`, and `as_ghz`, plus `From<Hertz> for c_ulong`. Under `CONFIG_COMMON_CLK`, `Clk` wraps `*mut bindings::clk` and exposes `get`, `as_raw`, `enable`, `disable`, `prepare`, `unprepare`, `prepare_enable`, `disable_unprepare`, `rate`, and `set_rate`. `OptionalClk` wraps optional clocks from `clk_get_optional` and derefs to `Clk`.

## Control Flow and State
Clock acquisition calls `clk_get` or `clk_get_optional` with a device and optional connection ID. Clock operations directly call the corresponding C API and convert integer errors through `to_result`/`from_err_ptr`. `Drop for Clk` calls `clk_put`, so both `Clk` and `OptionalClk` release their C references through RAII.

## State and Persistence Behavior
`Hertz` is a copyable value. `Clk` persists a C clock reference until drop. `OptionalClk` may contain a null underlying pointer per common-clk optional semantics, but it still exposes the same operations through `Deref`.

## Dependencies and Integration Points
The file depends on `ffi::c_ulong`, and conditionally on `Device`, `CStr`, error helpers, C clock bindings, and `Deref`. It is used by cpufreq policy setup through `Policy::set_clk`.

## Risks
Rate unit conversion truncates toward lower units and multiplication constructors do not check overflow. `Policy::set_clk` callers must keep the returned `Clk` alive while C uses the raw pointer. Optional clocks require C helpers to tolerate null handles for later operations.

## Test Signals
Doc examples cover frequency conversion and common clock configuration. No local KUnit tests are present; runtime testing requires a device with real or mock common clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/clk.rs -->
