<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-tng.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-tng.c

## Purpose
PCI platform driver for Intel Tangier/Edison SOF devices using the older Atom HiFi DSP path and IPC3 only. It supplies PCI resource mapping, IRQ setup, debugfs regions, firmware/topology defaults, Atom-specific DSP ops, and the single Tangier chip descriptor.

## Important APIs, Types, and Functions
`tangier_pci_probe()` is the local probe hook used by `sof_tng_ops`. It sets a 31-bit DMA mask, maps the LPE BAR by subtracting `IRAM_OFFSET`, optionally maps the IMR BAR, registers the Atom IRQ handler/thread, unmasks BUSY and masks DONE interrupts through `SHIM_IMRX`, and sets the default DSP mailbox offset. `sof_tng_ops` wires Atom run/reset/IPC/machine/stream/debug/firmware-loading callbacks into SOF core operations. `tng_chip_info`, `tng_desc`, `sof_tng_machines`, `tng_debugfs`, `sof_pci_ids[]`, and `snd_sof_pci_intel_tng_driver` are the data-driven integration surface.

## Control Flow, State, and Persistence
PCI match selects `tng_desc`, then generic `sof_pci_probe()` calls the descriptor ops. `tangier_pci_probe()` populates `sdev->num_cores`, `sdev->bar[DSP_BAR]`, optional `sdev->bar[IMR_BAR]`, `sdev->ipc_irq`, and `sdev->dsp_box.offset`. Persistent runtime state is held in `snd_sof_dev` and released by devm-managed mappings/IRQs and generic SOF PCI removal. Firmware loading uses memcpy-style block writes through generic iomem helpers and Atom ops.

## Dependencies and Integration
Depends on Atom DSP helpers (`atom_run`, `atom_reset`, `atom_send_msg`, IRQ handlers, mailbox/window offsets, DAI definitions, machine selection), `shim.h` register definitions, SOF PCI core, and Xtensa arch ops. It integrates with ACPI ID `INT343A`, `edison` machine driver selection, `sof-byt.ri`, `sof-byt.tplg`, and debugfs exposure for DMAC, SSP, IRAM, DRAM, and SHIM windows.

## Risks and Test Signals
Risks include the hard 31-bit DMA mask, BIOS IMR base sentinel handling, LPE BAR base arithmetic tied to `IRAM_OFFSET`, IRQ mask polarity errors, and reuse of Baytrail firmware/topology names for Tangier. Test signals include PCI probe on SST_TNG, valid LPE/IMR mappings, IRQ delivery through Atom handlers, firmware ready mailbox at `MBOX_OFFSET`, successful playback/capture over the three SSP DAIs, and debugfs region reads in D0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-tng.c -->
