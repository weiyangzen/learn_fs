# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/Kconfig

Purpose: defines build-time configuration options for Intel Platform Monitoring Technology drivers.

Important APIs/types/functions: `INTEL_PMT_CLASS` is an internal tristate selected by feature drivers. `INTEL_PMT_TELEMETRY` depends on `INTEL_VSEC` and selects discovery and class support. `INTEL_PMT_CRASHLOG` depends on `INTEL_VSEC` and selects class support. `INTEL_PMT_DISCOVERY` depends on `INTEL_VSEC` and selects class support. `INTEL_PMT_KUNIT_TEST` depends on discovery, KUnit, and a telemetry-compatible expression so tests can build with telemetry enabled or disabled.

Control flow: Kconfig selections determine which objects in the PMT Makefile are built. Telemetry selecting discovery means telemetry users also get feature discovery interfaces. Crashlog remains independent of telemetry but shares the class layer.

State and persistence: no runtime state. Kconfig state persists in the kernel build configuration and affects module availability/names.

Dependencies and integration points: integrates with `INTEL_VSEC`, PMT class, telemetry, crashlog, discovery, and KUnit infrastructure. Help text points to the sysfs ABI documentation for the class interface.

Risks: typo in help text says "Monitory" for telemetry, not functional. Selection dependencies can increase build footprint: enabling telemetry also enables discovery and class. KUnit dependency expression is intentionally broad and should be checked if telemetry APIs used by tests change.

Test signals: `allyesconfig`/`allmodconfig` should build all PMT modules. Minimal configs enabling telemetry/crashlog/discovery should pull in `intel_pmt_class`. KUnit config should produce `pmt-discovery-kunit`.
