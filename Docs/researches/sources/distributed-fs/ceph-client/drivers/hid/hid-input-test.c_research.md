# sources/distributed-fs/ceph-client/drivers/hid/hid-input-test.c

Defines KUnit tests for HID input battery status helpers. It verifies charge-status update semantics and power-supply status reporting for HID batteries.

`hid_test_input_update_battery_charge_status()` allocates a `struct hid_battery`, calls `hidinput_update_battery_charge_status()` with unrelated and charging usages, and checks handled flags plus `POWER_SUPPLY_STATUS_*` values. `hid_test_input_get_battery_property()` allocates fake HID, battery, and power-supply objects, sets `avoid_query`, and checks `hidinput_get_battery_property()` for unknown, charging, and discharging states. `hid_input_tests` and `hid_input_test_suite` register the KUnit suite named `hid_input`.

All state is test-local and KUnit-managed. Dependencies include KUnit, HID input internals available to the test build, power-supply status constants, and `struct hid_battery`.

Risks include dependence on static/internal HID input helpers and narrow coverage limited to status behavior rather than capacity scaling, querying, or real power-supply registration. Test signal is the `hid_input` KUnit suite passing, confirming unknown battery status masks charge state, reported battery status exposes charge/discharge, and unrelated usages are ignored.
