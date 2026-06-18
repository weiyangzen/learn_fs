# sources/distributed-fs/ceph-client/include/linux/extcon.h

Purpose: consumer-facing external connector ID/property definitions and notifier lookup API.

Important APIs/types/functions: connector type/id constants for USB, chargers, jacks, displays, misc connectors; property constants/ranges; `union extcon_property_value`; `extcon_get_state()`, property get/capability helpers, per-ID and all-connector notifier registration/devm variants, lookup helpers by name/device tree phandle, `extcon_get_edev_name()`, and deprecated `struct extcon_specific_cable_nb`.

Control flow: consumers obtain an `extcon_dev`, query current state/properties, and register notifiers for connector changes. Provider updates are delivered through extcon core. Config-off stubs return neutral values or errors depending on lookup/managed operation.

State/persistence: runtime connector state/properties and notifier registrations. No disk persistence.

Dependencies/integration: device model, device tree nodes/phandles, notifier blocks, USB/charger/audio/display drivers, provider API.

Risks/test signals: risks are ID/property range drift, ambiguous config-off success stubs, notifier leaks, phandle lookup failures, and deprecated API users. Test connector state changes, property capabilities, all-vs-specific notifiers, DT lookup, devm unregister, and type/range validation.
