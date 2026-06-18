# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_typec.h

## Purpose
`cros_ec_typec.h` defines private data structures shared by the Chrome EC Type-C driver and related local Type-C helper modules.

## Important APIs, Types, and Functions
- The anonymous altmode enum indexes DisplayPort, Thunderbolt, USB4, and max altmode slots.
- `struct cros_typec_altmode_node` links registered `struct typec_altmode` objects in partner or plug mode lists.
- `struct cros_typec_data` stores device-global EC Type-C driver state, including EC pointer, port count, PD control version, ports array, notifier/work item, and feature flags.
- `struct cros_typec_port` stores per-port Type-C class objects, switch/mux/retimer/role-switch handles, mux state, current flags/role, identities, discovery buffers, altmode lists, partner PD capability objects, and backpointer to global data.

## Control Flow
The header does not implement control flow. `cros_ec_typec.c` allocates and populates these structures during probe, updates them from EC notifications/workqueue processing, and tears them down during disconnect or remove. Local altmode/VDM helpers use the same structures to access port state.

## State and Persistence
This header defines all long-lived state for the Type-C driver. Global state lives for the platform device lifetime. Per-port partner/cable/PD/altmode state changes dynamically as connections, hard resets, and discovery events occur.

## Dependencies and Integration Points
It depends on Linux list/notifier/workqueue APIs, Chrome EC protocol definitions, USB PD identity types, USB role switch, Type-C class, altmode, mux, and retimer APIs. It is included by `cros_ec_typec.c` and likely companion files handling VDMs and altmodes.

## Risks and Edge Cases
Because `ports` is fixed to `EC_USB_PD_MAX_PORTS`, probe clamps EC-reported port counts before filling it. The lists require proper initialization before altmode registration and proper cleanup on errors. State fields such as `mux_flags`, `role`, and discovery-done booleans are cache/coherency points between EC status and Type-C class objects.

## Test Signals
No direct tests target this header. Compile coverage from the Type-C driver and runtime creation/removal of ports, partners, cables, and altmodes exercise the structure contracts.
