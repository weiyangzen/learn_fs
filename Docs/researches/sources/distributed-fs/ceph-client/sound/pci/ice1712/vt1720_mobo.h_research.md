# sources/distributed-fs/ceph-client/sound/pci/ice1712/vt1720_mobo.h

## Purpose
`vt1720_mobo.h` declares motherboard-specific VT1720 descriptions, subdevice IDs, and the exported card-info table.

## Important APIs, Types, and Functions
- `VT1720_MOBO_DEVICE_DESC` aggregates Albatron, Chaintech, and Shuttle model descriptions.
- `VT1720_SUBDEVICE_*` constants identify K8X800, ZNF3-150, ZNF3-250, 9CJS, and SN25P boards.
- `extern struct snd_ice1712_card_info snd_vt1720_mobo_cards[]` exposes the table implemented in `vt1720_mobo.c`.

## Control Flow
The header has no executable flow. It participates in compile-time registration and subvendor-based dispatch in `vt1720_mobo.c`.

## State and Persistence
No state is stored. Constants preserve the hardware matching contract.

## Dependencies and Integration Points
Consumers must include ICE1712 card-info declarations before using the extern table. The IDs integrate with PCI subsystem matching performed by the Envy24HT core.

## Risks and Test Signals
Incorrect IDs lead to unsupported board probes or wrong EEPROM defaults. Test signals are correct matching and model names for all five motherboards.
