# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1.h

Purpose: defines the Global 1 register map, bit masks, table operation encodings, ATU/VTU/STU data encodings, monitor-control constants, statistics op constants, and prototypes for Global1, ATU, VTU, STU, reset, PPU, priority, and statistics helpers.

Important APIs/types/functions: constants cover status, MAC registers, control, VTU operation/data, ATU control/operation/data/MAC, priority maps, monitor/MGMT control, control2, and stats registers. Prototypes export base accessors plus family-specific reset, EEPROM, PPU, frame-size, stats, monitor, RMU, ATU, VTU, STU, and IRQ helpers.

Control flow: no executable code. The header is the contract that lets ops tables select the correct implementation for each switch family.

State and persistence: described state is hardware-resident: ATU MAC/FID entries, VTU VLAN membership, STU state, counters, PPU status, and reset/configuration bits.

Dependencies/integration: includes `chip.h` for shared types and enum values. It is consumed by Global1 implementation files, devlink snapshots, PTP/management setup, and switchdev/bridge integration.

Risks: many register offsets are aliased by chip generation, such as MAC bytes versus ATU/VTU FID registers, so users must call the right helper in the right hardware context. Bitfield comments encode non-obvious FID packing.

Test signals: build coverage across enabled chip families, runtime ATU/VTU programming, bridge VLAN/STP behavior, statistics reads, and interrupt handling for ATU/VTU violations.
