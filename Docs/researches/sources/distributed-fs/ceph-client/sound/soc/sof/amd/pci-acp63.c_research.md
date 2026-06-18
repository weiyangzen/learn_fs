# sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-acp63.c

Purpose: PCI binding and SOF descriptor for AMD ACP6.3 platforms.

Important APIs/types/functions: `acp63_chip_info` defines ACP6.x register offsets, interrupt registers, error registers, SRAM PTE offset, hardware semaphore, fusion runstall, probe register, SoundWire max link count/address, and register range. `acp63_desc` defines machine tables, alternate SoundWire machines, firmware/topology paths/names, IPC3 support, nocodec topology, ops pointer, and ops init. `acp63_pci_probe()` filters by PCI revision and AMD ACP config before calling `sof_pci_probe()`.

Control flow: PCI match accepts AMD ACP device ID, then probe rejects non-ACP63 revisions and non-SOF machine-config flags. Successful probes pass `acp63_desc` through `driver_data` to generic SOF PCI probe.

State and persistence: static descriptor data persists for module lifetime; runtime state is created by common ACP probe.

Dependencies and integration points: AMD machine config, ACPI machine tables, SoundWire alt machine tables, SOF PCI device glue, and ACP common namespace.

Risks: revision filtering is strict. Register range and SoundWire ACPI address must match firmware/ACPI; wrong descriptor fields break common probe or IRQ handling.

Test signals: PCI enumeration on ACP63, config flag gating, SoundWire ACPI scan, firmware `sof-acp_6_3.ri`, and topology selection.
