# sources/distributed-fs/ceph-client/drivers/hsi/hsi_core.c

## Purpose
Implements the Linux HSI bus core: bus registration/matching, controller and port allocation/registration, client creation from board info or device tree, message allocation/freeing, async dispatch, port claim/release, event notifier plumbing, and channel-name lookup.

## Important APIs, Types, and Functions
- Bus type `hsi_bus_type` with modalias, uevent, OF/name matching, and device attributes.
- Client/controller APIs: `hsi_new_client()`, `hsi_register_controller()`, `hsi_unregister_controller()`, `hsi_register_client_driver()`, `hsi_alloc_controller()`, `hsi_put_controller()`.
- Message APIs: `hsi_alloc_msg()`, `hsi_free_msg()`, `hsi_async()`.
- Port APIs: `hsi_claim_port()`, `hsi_release_port()`, `hsi_register_port_event()`, `hsi_unregister_port_event()`, `hsi_event()`, `hsi_get_channel_id_by_name()`.
- OF helper `hsi_add_clients_from_dt()` registers `hsi_char` and child client nodes.

## Control Flow
Postcore init registers the HSI bus. Controller drivers allocate controllers with initialized ports and dummy callbacks, then register them. Registration adds controller and port devices and scans static board info. DT port code can add clients by parsing mode, speed, flow, arbitration, and channel IDs/names. Clients must claim a port before async transfers; `hsi_async()` verifies the claim and delegates to the controller port callback. Event registration attaches a client notifier to a port blocking notifier chain.

## State and Persistence
Controller, port, and client objects are kernel devices with release callbacks. Port state includes claim count, sharing flag, mutex, and notifier chain. Client TX/RX channel arrays are duplicated and freed on device release. No disk persistence.

## Dependencies and Integration Points
Uses Linux driver core, OF helpers, notifier chains, scatterlists through HSI messages, module reference counting, and static board info from `hsi_boardinfo.c`. Controller drivers supply actual port operations.

## Risks and Test Signals
Risks include shared-port claim semantics, module reference imbalance on release, async callbacks occurring before `hsi_async()` returns, malformed DT properties, and null channel names in lookup. Test signals include bus modalias autoloading, DT client enumeration, static board client enumeration, shared/exclusive claim behavior, event callbacks in interrupt context, and cleanup order on unregister.
