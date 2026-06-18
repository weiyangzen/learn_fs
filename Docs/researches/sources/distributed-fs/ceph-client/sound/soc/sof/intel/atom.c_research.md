# sources/distributed-fs/ceph-client/sound/soc/sof/intel/atom.c

Purpose: `atom.c` implements shared IPC, reset, run, dump, machine-selection, and DAI support for Atom-class SOF platforms using the older HiFi EP SHIM interface. Baytrail, Cherrytrail, Braswell, and Merrifield-style code can reuse these exported helpers.

Important APIs: exported functions include `atom_irq_handler()`, `atom_irq_thread()`, `atom_send_msg()`, `atom_get_mailbox_offset()`, `atom_get_window_offset()`, `atom_run()`, `atom_reset()`, `atom_dump()`, `atom_machine_select()`, `atom_set_mach_params()`, and the `atom_dai[]` SSP DAI table. Internal helpers `atom_host_done()` and `atom_dsp_done()` implement doorbell completion.

Control flow: the hard IRQ reads `SHIM_IPCX` and `SHIM_IPCD`, masks DONE or BUSY interrupts, and wakes the threaded IRQ. The thread processes DSP replies under `sdev->ipc_lock`, calls `snd_sof_ipc_process_reply()`, clears DONE, handles firmware-originated messages or panic magic, then acknowledges BUSY and unmasks the next interrupt. `atom_send_msg()` writes the host mailbox and rings `SHIM_BYT_IPCX_BUSY`. Reset stalls the DSP, sets reset/vector bits, then releases reset for firmware loading. Run clears stall and polls `PWAITMODE`.

State and persistence behavior: mailbox and window offsets are fixed to `MBOX_OFFSET`; panic/oops state is read from `sdev->dsp_oops_offset`. Machine selection mutates `sof_pdata->tplg_filename` and machine params. On BYT-CR systems, it rewrites topology names from the matched ACPI machine to an `ssp0` variant.

Dependencies and integration: this file depends on SOF IPC core helpers, Xtensa panic printing, ACPI machine tables, Intel DSP config, and Atom SHIM register definitions. It integrates with `byt.c` through `snd_sof_dsp_ops`.

Risks and test signals: interrupt races are the main risk, especially masking/unmasking DONE and BUSY around reply processing. Topology filename fixups assume a `.tplg` extension and can fail allocation. Test signals include IPC round trips, panic dump readability, BYT-CR SSP0 topology selection, suspend/resume interrupt unmask state, and all six exported SSP DAI names appearing as expected on Cherrytrail.
