# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_hw.h

Purpose: Defines the public firmware/hardware API surface and shared enums for the Prestera driver.

Important APIs/types/functions: Contains enums for accept frame type, FDB flush modes, MAC/link modes, port types/transceivers/FEC/duplex, STP states, policer types, CPU-code counter type, vTCAM direction, and counter clients. Declares all `prestera_hw_*` switch, port, VLAN, FDB, bridge, vTCAM, counter, SPAN, router, VR/LPM/NH, event, RX/TX, LAG, trap counter, policer, flood-domain, and MDB APIs.

Control flow: No implementation. Higher layers call these APIs; `prestera_hw.c` implements firmware message transport and decoding.

State and persistence: No direct state. The declarations operate on `prestera_switch`, `prestera_port`, and hardware object structures owned elsewhere.

Dependencies/integration: Includes `prestera_acl.h` for ACL action/match contracts and forward-declares many shared structures. This header is the integration boundary between feature modules and firmware commands.

Risks: Enum numeric values are ABI-facing and must remain aligned with firmware and ethtool mappings. Broad inclusion can amplify rebuilds and coupling. API changes affect many driver subsystems.

Test signals: Kernel compile coverage, ABI layout checks in `prestera_hw.c`, and subsystem tests for every declared hardware API family.
