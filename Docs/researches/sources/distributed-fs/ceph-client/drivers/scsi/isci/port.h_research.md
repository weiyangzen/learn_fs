# sources/distributed-fs/ceph-client/drivers/scsi/isci/port.h

Purpose: declares the ISCI port contract shared by host, PHY, request, and remote-device code. It defines the port state container, public port lifecycle and event APIs, state IDs, property structures, not-ready reasons, and request-count helpers.

Important APIs/types/functions: `struct isci_port` holds controller ownership, libsas-facing remote-device list, state-machine object, reset state, PHY masks, dummy scheduler resources, request counters, and MMIO pointers. `enum sci_port_states` enumerates stopped, stopping, ready, ready substates, resetting, and failed. `struct sci_port_properties` and nested endpoint properties report local/remote SAS addresses, protocols, and PHY mask. Public prototypes cover construction, start/stop, PHY add/remove, link up/down, I/O start/complete, hard reset, broadcast change, hang-detection timeout, SAS address accessors, and libsas formed/deformed callbacks.

Control flow: the header does not execute code beyond small helpers. `sci_port_decrement_request_count()` guards request-count underflow with `WARN_ONCE()`, while `sci_port_active_phy()` tests active membership. The declared functions are implemented mostly in `port.c` and are called by host startup, PHY event handling, remote-device I/O, and libsas callbacks.

State and persistence: `struct isci_port` is the authoritative in-memory state for a logical/physical port. It tracks transient masks, counters, reset status, timer state, not-ready reasons, and hardware-resource reservations; no persistent storage is defined here. The `IPORT_RESET_PENDING` bit is used as a wait condition for hard-reset completion.

Dependencies and integration points: includes libsas plus ISCI local headers for host, SAS, and PHY types. Forward declarations avoid cycles with request and remote-device types. MMIO pointer members tie the port to SCU register structs from `registers.h`.

Risks and test signals: because the struct is shared across multiple driver subsystems under `ihost->scic_lock`, field ownership must remain clear during refactors. Request-count underflow warnings, reset wait completion, state-name coverage, and compile-time prototype consistency are key signals. Tests should exercise all declared state transitions through `port.c`, plus SATA readiness checks through `isci_ata_check_ready()`.
