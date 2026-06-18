<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-tgl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-tgl.c

## Purpose
PCI glue for Intel Tiger Lake generation SOF HDA platforms and close derivatives: TGL-LP, TGL-H, Elkhart Lake, Alder/Raptor Lake desktop/mobile/N variants. It maps PCI IDs to `sof_dev_desc` records that drive generic SOF PCI/HDA probe, firmware/topology file selection, IPC version selection, ACPI machine matching, and platform ops initialization.

## Important APIs, Types, and Functions
The file defines static `sof_dev_desc` instances `tgl_desc`, `tglh_desc`, `ehl_desc`, `adls_desc`, `adl_desc`, `adln_desc`, `rpls_desc`, and `rpl_desc`. Each points at a chip descriptor from `tgl.c`, HDA ops from `sof_tgl_ops`, `sof_tgl_ops_init()`, and `hda_ops_free()`. `sof_pci_ids[]` binds Intel HDA PCI device IDs to those descriptors. The `snd_sof_pci_intel_tgl_driver` uses `hda_pci_intel_probe`, `sof_pci_remove`, `sof_pci_shutdown`, and `sof_pci_pm`.

## Control Flow, State, and Persistence
There is no mutable state in this file. Probe is delegated to the generic HDA PCI path, which receives the matched `sof_dev_desc` via PCI match data. The descriptor selects ACPI machine tables, alternate SoundWire tables where available, firmware and topology paths for IPC3 and IPC4, default firmware filenames, nocodec topology, DSP ops, and resource indexes. Runtime state is allocated by the PCI/HDA/SOF core after descriptor selection.

## Dependencies and Integration
Depends on Linux PCI and module APIs, SOF PCI device helpers, ACPI machine match tables, and `hda.h` exports. It integrates with `tgl.c` for DSP hardware descriptors and ops, generic HDA probe/remove/shutdown, firmware loading paths under `intel/sof*`, topology selection, SoundWire alternate machine matching, and DSP-less HDaudio mode.

## Risks and Test Signals
Main risks are table-driven mismatches: wrong `chip_info` for a PCI ID, incorrect firmware path for IPC4 platform subdirectory, ACPI machine table mismatch, or enabling `dspless_mode_supported` beyond HDaudio-only expectations. Test signals are successful PCI probe for every listed device ID, correct IPC3/IPC4 firmware filename selection, SoundWire alternate machine selection on SDW systems, nocodec fallback loading, suspend/resume through `sof_pci_pm`, and module namespace resolution for HDA generic/common/CNL and PCI helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-tgl.c -->
