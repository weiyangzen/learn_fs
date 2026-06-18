# sources/distributed-fs/ceph-client/include/linux/ptp_pch.h

Purpose: declares helper accessors for the PCH PTP hardware block behind PCI devices.

Important APIs and types: functions write channel control and event registers, read source UUID low/high words, read RX/TX snapshot timestamps, and set station address for a `pci_dev`.

Control flow: a PCH PTP or network driver calls these helpers to configure timestamp channels, clear/read events, retrieve captured timestamps, and program the station address used by hardware timestamping.

State and persistence: state is hardware register state in the PCI device. Snapshot registers reflect transient packet timestamp events.

Dependencies and integration points: depends on PCI device access and PCH-specific PTP hardware. Integrates timestamp capture with network drivers on affected platforms.

Risks and test signals: risks include register ordering, stale event bits, endianness/width issues reading 64-bit snapshots, and invalid station address programming. Test TX/RX timestamp capture, event clear/write behavior, UUID reads, PCI remove/suspend, and station address updates.
