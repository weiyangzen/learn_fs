# sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/Makefile

Purpose: Builds optional KUnit test modules for the WMI helper code.

Important APIs and types: `wmi_marshalling_kunit-y := marshalling_kunit.o` and `wmi_string_kunit-y := string_kunit.o` define test module objects. Config-gated `obj-*` entries add each module.

Control flow: Kbuild includes the test objects when their Kconfig symbols are enabled.

State and persistence: No runtime state. It is build metadata only.

Dependencies and integration points: Linked from the parent WMI Makefile via `obj-y += tests/`. The comment path is stale and says `drivers/platform/x86/wmi/tests`.

Risks: If the object names or config symbols drift from Kconfig, tests silently stop building. Test modules depend on internal helper visibility and namespace imports.

Test signals: `make ... CONFIG_ACPI_WMI_MARSHALLING_KUNIT_TEST=m CONFIG_ACPI_WMI_STRING_KUNIT_TEST=m` produces the two KUnit modules and their suites run under KUnit.
