# sources/distributed-fs/ceph-client/sound/soc/sof/intel/byt.c

Purpose: `byt.c` provides the ACPI platform driver and operation tables for Baytrail, Baytrail-CR, Braswell, and Cherrytrail SOF devices. It combines Atom shared helpers with platform-specific resource mapping, debug maps, DMA mask setup, ACPI descriptors, and probe filtering.

Important APIs and structures: key functions are `byt_acpi_probe()`, `byt_suspend()`, `byt_resume()`, `byt_remove()`, `byt_reset_dsp_disable_int()`, and `sof_baytrail_probe()`. Important static objects include BYT and CHT debugfs maps, `sof_byt_ops`, `sof_cht_ops`, `byt_chip_info`, `cht_chip_info`, three `sof_dev_desc` instances for BYT, BYT-CR, and CHT, and the ACPI match table for `80860F28` and `808622A8`.

Control flow: `sof_baytrail_probe()` verifies the ACPI ID, consults `snd_intel_acpi_dsp_driver_probe()`, switches to the BYT-CR descriptor if board quirks match, and calls `sof_acpi_probe()`. `byt_acpi_probe()` gets chip info, forces a 31-bit DMA mask, maps LPE and optional IMR resources, requests the host IPC IRQ with Atom handlers, enables BUSY while masking DONE by default, and sets `sdev->dsp_box.offset`.

State and persistence behavior: descriptor data persists firmware path, topology path, default firmware filename, no-codec topology, IRQ/resource indexes, and IPC3-only support. Runtime state includes mapped DSP/IMR BARs, IRQ, mailbox offsets, and interrupt masks. Suspend, remove, and reset paths explicitly reset the DSP and disable both host and DSP interrupt directions.

Dependencies and integration: it depends on Atom helpers from `atom.c`, SOF ACPI device glue, ACPI machine tables, Intel DSP selection, and BYT-CR quirk detection.

Risks and test signals: IMR may be absent or bogus, and the code deliberately ignores BIOS sentinel base values. BYT-CR topology and IRQ-index differences are fragile. Test signals include correct descriptor selection, successful ioremap of LPE, optional IMR handling, IPC3 firmware load for `sof-byt.ri` and `sof-cht.ri`, debugfs region access, and suspend/resume preserving interrupt state.
