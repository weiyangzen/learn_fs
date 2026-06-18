# sources/distributed-fs/ceph-client/sound/soc/sof/intel/bdw.c

Purpose: `bdw.c` is the complete ACPI platform driver and DSP operation implementation for Broadwell SOF. It handles MMIO mapping, PCI power setup, IPC, debug dumps, machine selection, DAI exposure, and ACPI probe registration for device `INT3438`.

Important APIs and structures: the file defines `bdw_probe()`, `bdw_run()`, `bdw_reset()`, `bdw_set_dsp_D0()`, `bdw_irq_handler()`, `bdw_irq_thread()`, `bdw_send_msg()`, mailbox/window offset helpers, `bdw_machine_select()`, `bdw_set_mach_params()`, `bdw_dai[]`, `sof_bdw_ops`, `bdw_chip_info`, `sof_acpi_broadwell_desc`, and `snd_sof_acpi_intel_bdw_driver`.

Control flow: probe maps LPE and PCI resources, records DSP and mailbox BARs, requests the platform IPC IRQ, forces the DSP into D0, sets a 31-bit DMA mask, and sets the firmware-ready mailbox offset. `bdw_set_dsp_D0()` is the hardware bring-up sequence: disable/enable gating bits, set PCI PM D0, configure clocks and SSP, reset the core, configure power gating, clear IPC registers, and enable interrupts. IPC handling follows the older SHIM model: the IRQ handler detects BUSY/DONE, the thread masks, processes replies or firmware messages/panics, and acknowledges via `bdw_host_done()` or `bdw_dsp_done()`.

State and persistence behavior: runtime state lives in mapped BAR pointers, `sdev->mmio_bar`, `sdev->mailbox_bar`, `sdev->dsp_oops_offset`, IRQ registration, ACPI selected topology, and machine params. Debugfs exposes DMAC, SSP, IRAM, DRAM, and SHIM windows.

Dependencies and integration: this driver depends on SOF ACPI probe infrastructure, Intel DSP driver selection, Xtensa dumps, SOF stream helpers, and ACPI machine tables. It imports the SOF Xtensa and ACPI namespaces.

Risks and test signals: Broadwell is explicitly less robust for DMA and suspend/resume, so power sequencing and interrupt mask handling are high risk. Test with ACPI driver selection arbitration, firmware boot, IPC reply/message handling, panic dump, no-codec topology fallback, runtime/system suspend, and DMA mask correctness on real BDW hardware or targeted emulation.
