# sources/distributed-fs/ceph-client/lib/kunit/Kconfig

Purpose: defines build-time configuration for KUnit core, debugfs integration, self-tests, examples, autorun/filter defaults, timeouts, and UML PCI support.

Important symbols: `KUNIT`, `KUNIT_DEBUGFS`, `KUNIT_FAULT_TEST`, `KUNIT_TEST`, `KUNIT_EXAMPLE_TEST`, `KUNIT_ALL_TESTS`, `KUNIT_DEFAULT_ENABLED`, `KUNIT_AUTORUN_ENABLED`, `KUNIT_DEFAULT_FILTER_GLOB`, `KUNIT_DEFAULT_FILTER`, `KUNIT_DEFAULT_FILTER_ACTION`, `KUNIT_DEFAULT_TIMEOUT`, and `KUNIT_UML_PCI`.

Control flow: Kconfig dependencies and defaults determine which KUnit objects compile and how runtime module/core parameters default. `KUNIT_ALL_TESTS` fans into individual tests when dependencies are satisfied. Debugfs depends on `DEBUG_FS`; fault tests avoid UML and default off when panic-on-oops would make them disruptive.

State and persistence: persistent kernel configuration state influences compiled code and default runtime parameters.

Dependencies and integration: integrates with the kernel Kconfig system, UML PCI selection, debugfs availability, and KUnit Makefile object selection.

Risks: enabling all tests in production-like builds can run boot-time tests unexpectedly; default autorun/filter values alter boot behavior; fault tests intentionally produce BUG-like traces.

Test signals: `allnoconfig`, KUnit-enabled, UML, module, and built-in config matrix builds; validation that default filter strings propagate into executor parameters.
