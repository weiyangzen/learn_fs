# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpsw.h

Purpose: Public local API header for DPAA2 Data Path Switch management. It defines switch capabilities, option bits, public configuration structures, enums, event masks, and prototypes implemented by `dpsw.c`.

Important APIs and types: Defines limits such as `DPSW_MAX_PRIORITIES`, `DPSW_MAX_IF`, and `DPSW_MAX_DPBP`. Public structs model switch attributes, control-interface attributes and queue configuration, link configuration/state, TCI/STP, interface attributes, VLAN membership, FDB unicast/multicast entries, FDB dump entries, egress flooding, ACL keys/results/entries, and reflection rules. Enums cover component type, flooding/broadcast mode, queue type, destination type, accepted frames, counters, learning mode, ACL actions, and reflection filters.

Control flow and state: The header defines the intended call sequence: open a switch object, query attributes, configure interfaces/link/VLAN/FDB/ACL/control queues, enable the object or interfaces as needed, then close. It does not store state; all actual switch state lives in the MC object and is accessed through tokens.

Dependencies and integration points: Forward-declares `struct fsl_mc_io` and relies on Linux network and integer types from includers. It is consumed by DPAA2 Ethernet/switch management code and by `dpsw-cmd.h` for command ABI sizing.

Risks: Many structures contain arrays sized for `DPSW_MAX_IF`; callers must set `num_ifs` consistently. ACL entry usage requires a prepared DMA buffer and stable `key_iova`. Counter and learning mode enums map directly to firmware values, so value changes would be ABI-breaking. `DPSW_STP_STATE_DISABLED` and `DPSW_STP_STATE_BLOCKING` both map to zero in this snapshot, which may be intentional firmware encoding but is a semantic hazard for callers.

Test signals: Compile coverage across all consumers, firmware API compatibility checks, and integration tests that exercise public structures through `dpsw.c`: VLAN add/remove, FDB add/remove/dump, ACL redirect/drop/accept, link state, counters, control-interface RX/TX error queues, and reflection.
