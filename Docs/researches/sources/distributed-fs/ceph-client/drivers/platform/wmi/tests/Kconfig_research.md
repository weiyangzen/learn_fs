# sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/Kconfig

Purpose: Adds KUnit configuration options for WMI marshalling and WMI string conversion tests.

Important APIs and types: `ACPI_WMI_MARSHALLING_KUNIT_TEST` and `ACPI_WMI_STRING_KUNIT_TEST` are tristate options depending on `KUNIT`, defaulting to `KUNIT_ALL_TESTS`, and hidden when all KUnit tests are enabled.

Control flow: When selected, the corresponding objects in `tests/Makefile` build and register KUnit suites at module/init time.

State and persistence: No runtime state. The file influences build/test configuration only.

Dependencies and integration points: Sourced from `drivers/platform/wmi/Kconfig` under `if ACPI_WMI`, so tests are tied to the WMI core menu. Help text points to kernel KUnit documentation.

Risks: Tests are unavailable if ACPI-WMI is disabled even though parts of the helper logic are mostly pure conversion code. Maintaining default `KUNIT_ALL_TESTS` keeps broad CI coverage but can increase build time.

Test signals: Enabling each config builds `wmi_marshalling_kunit` or `wmi_string_kunit`; KUnit output contains suites named `wmi_marshalling` and `wmi_string`.
