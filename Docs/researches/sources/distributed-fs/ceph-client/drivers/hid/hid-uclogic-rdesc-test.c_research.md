# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-rdesc-test.c

Purpose: KUnit tests for UC-Logic report descriptor template substitution, focused on `uclogic_rdesc_template_apply()`.

Important APIs, types, and functions: `struct uclogic_template_case` defines a template buffer, size, parameter list, and expected result. Test data covers empty/small templates, templates without placeholders, incomplete placeholders at the end, pen placeholders for all or some parameters, frame button placeholders, and missing parameter IDs. `hid_test_uclogic_template()` calls `uclogic_rdesc_template_apply()`, asserts allocation success, compares the full result buffer, then frees it.

Control flow: a KUnit array parameter generator runs all template cases. The test validates that pen placeholders become little-endian 32-bit values and frame button placeholders become HID Usage Maximum items with little-endian 16-bit values.

State and persistence: only temporary KUnit/test allocations and the returned kmalloc descriptor copy exist.

Dependencies and integration: imports the `EXPORTED_FOR_KUNIT_TESTING` namespace and includes `hid-uclogic-rdesc.h`. The production function is exported only for KUnit visibility.

Risks: tests verify substitution mechanics but not semantic validity of the large static descriptors. Boundary cases around placeholder heads at buffer end are covered.

Test signals: run the `hid_uclogic_rdesc_test` KUnit suite. Failures indicate descriptor template replacement regressions that would affect parameter-derived tablet descriptors.
