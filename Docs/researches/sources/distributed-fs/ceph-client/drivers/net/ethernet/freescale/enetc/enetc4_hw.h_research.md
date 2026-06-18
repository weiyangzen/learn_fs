# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_hw.h

Purpose: Defines ENETC revision 4 hardware register offsets, device IDs, and bit fields that are not already covered by the original ENETC hardware header. It is a register contract used by ENETC4 PF, PPM, ethtool, debugfs, and common core code.

Important constants and macros: Identifies NXP ENETC vendor/PF/PPM device IDs. Station-interface macros cover LSO segmentation flag masks and capability registers. Port macros cover SI enable, pause thresholds, discard counters, promiscuous MAC/VLAN modes, RSS keys, MAC/VLAN filtering capabilities, SI primary MAC and anti-spoofing registers, hash filters, port/MAC capabilities, speed configuration, MAC command configuration, maximum frame length, internal/external MDIO bases, interrupt events, pause quanta, single-step timestamp configuration, extensive MAC RX/TX counters, interface mode, and pseudo-MAC counters. Field helpers use `BIT`, `GENMASK`, and `FIELD_PREP`.

Control flow and state: No executable flow. The macros represent hardware state addressed by MMIO reads/writes elsewhere. For example, `ENETC4_PM_SINGLE_STEP()` fields are written by the one-step PTP timestamp path, hash filter registers are read by debugfs, and LSO flag masks are set during SI configuration.

Dependencies and integration points: Included by `enetc.h` and code that needs ENETC4-specific registers. Complements `enetc_hw.h`; comments state that shared ENETC v1 registers remain defined there. Integrates with PCI ID matching through driver-data selection in `enetc.c`.

Risks: Register offset mistakes cause silent hardware misconfiguration. Some macros take a MAC or SI index and compute offsets; callers must pass indexes within hardware-supported ranges. ENETC4 pseudo-MAC has a distinct counter block, so normal MAC register helpers must respect `ENETC_SI_F_PPM`. Speed and interface mode bitfield macros must match hardware units and encoding.

Test signals: ENETC4 PF/PPM probe with correct PCI IDs, ethtool counter reads, debugfs hash/promiscuous reads, one-step timestamp operation through `PM_SINGLE_STEP`, LSO behavior after `SILSOSFMR` programming, MDIO access through ENETC4 bases, and register readback tests for MAC command/configuration fields.
