# sources/distributed-fs/ceph-client/drivers/greybus/control.c

Purpose: Greybus interface control-protocol implementation. It owns the control connection and provides synchronous operations for version negotiation, manifest retrieval, CPort lifecycle notifications, bundle/interface PM, and mode switching.

Important APIs and functions: `gb_control_create`, `enable`, `disable`, `suspend`, `resume`, `add`, `del`, `get`, `put`, and mode-switch helpers manage the control device. Operation helpers include version and bundle-version queries, manifest size/data reads, connected/disconnected/disconnecting notifications, mode switch, bundle suspend/resume/deactivate/activate, interface suspend/deactivate prepare, and hibernate abort.

Control flow: enable brings the control connection up in TX mode, negotiates protocol version, sets feature flags for bundle version and activation, and disables the connection on failure. Operation helpers mostly call `gb_operation_sync`; disconnecting and mode-switch use explicit core operations. Disable chooses normal or forced connection teardown depending on interface disconnected state.

State and persistence: `struct gb_control` stores protocol version, feature flags, vendor/product strings, device object, interface pointer, and control connection. Sysfs exposes vendor and product strings. Device release destroys the connection and frees strings/control.

Dependencies and integration: depends on Greybus operation core, connection core, interface and bundle structures, sysfs device model, and Greybus protocol request/response definitions.

Risks: protocol feature detection is partly version-based and partly quirk-based. PM status codes must be mapped correctly to Linux errno. Control connection failure blocks manifest parsing and bundle setup.

Test signals: successful version negotiation, manifest retrieval, bundle version population, PM operation status handling, and connection teardown behavior during disconnects and mode switches.
