# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/Makefile

Purpose: maps PMT Kconfig symbols to module/object composition.

Important APIs/types/functions: builds `pmt_class.o` from `class.o`, `pmt_telemetry.o` from `telemetry.o`, `pmt_crashlog.o` from `crashlog.o`, `pmt_discovery.o` from `discovery.o features.o`, and `pmt-discovery-kunit.o` from `discovery-kunit.o`.

Control flow: kernel build includes each object according to its `CONFIG_INTEL_PMT_*` symbol. The object names align with module names described in Kconfig help.

State and persistence: no runtime state. Build output composition persists in generated kernel modules or built-in objects.

Dependencies and integration points: depends on Kconfig to select symbols and on source files in the same directory. Discovery links `features.o`, which supplies feature names/layouts referenced by discovery and KUnit code.

Risks: changing module object names can break module aliases or expected help text. Forgetting to include `features.o` with discovery would break symbols used by discovery and tests.

Test signals: build with each `CONFIG_INTEL_PMT_*=m/y` and verify expected module/object names. KUnit build should include only `discovery-kunit.o` for the test module.
