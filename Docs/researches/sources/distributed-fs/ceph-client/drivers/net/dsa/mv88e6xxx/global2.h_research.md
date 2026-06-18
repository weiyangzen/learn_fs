# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2.h

Purpose: defines the Global 2 register map, command encodings, data masks, scratch/GPIO register selectors, interrupt bits, watchdog bits, AVB/PTP window constants, SMI PHY command fields, and public prototypes for Global2 helpers and ops structures.

Important APIs/types/functions: constants cover interrupt source/mask, management enable, device mapping, trunk tables, IRL commands, PVT, switch MAC, ATU stats, EEPROM, AVB command/data, SMI PHY command/data, scratch/misc, watchdog, QoS, and misc port-width mode. Prototypes export Global2 accessors, EEPROM, PVT, IRQ, MDIO IRQ, AVB/watchdog/GPIO ops, scratch SMI muxing, and ATU stats.

Control flow: no executable flow. The header centralizes hardware encodings used by `global2.c`, `global2_avb.c`, `global2_scratch.c`, `hwtstamp.c`, and PHY/PCS code.

State and persistence: describes both volatile register state and persistent EEPROM data. Scratch straps/config registers reflect board/chip configuration and may gate SerDes/SMI/GPIO behavior.

Dependencies/integration: includes `chip.h`; exported ops are selected by chip family tables and consumed by DSA switch setup, MDIO, PTP, GPIO, devlink, and watchdog paths.

Risks: multiple families overload the same offsets with different meanings, especially watchdog and AVB command encodings. Misusing field widths can address the wrong port or external/internal PHY bus.

Test signals: compile coverage, per-family smoke tests for EEPROM, AVB/PTP, SMI PHY, watchdog, scratch GPIO, and interrupt masks.
