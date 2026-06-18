# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pic.c

Purpose: initializes and operates PowerMac interrupt controllers. It supports old 32-bit Apple PIC variants in Grand Central, OHare, Heathrow/Gatwick, and newer MPIC/OpenPIC controllers, including BootX and OldWorld interrupt-map workarounds and sleep-time interrupt masking.

Important APIs/types/functions: key globals are `of_irq_workarounds`, `of_irq_dflt_pic`, `pmac_irq_hw`, `ppc_lost_interrupts`, `ppc_cached_irq_mask`, `pmac_irq_cascade`, and `pmac_pic_host`. Public entry points are `pmac_pic_init` and, on old 32-bit systems, `of_irq_parse_oldworld`. Old PIC operations are `pmac_startup_irq`, `pmac_mask_irq`, `pmac_unmask_irq`, `pmac_ack_irq`, `pmac_mask_and_ack_irq`, `pmac_retrigger`, and `pmac_pic_get_irq`. MPIC setup uses `pmac_setup_one_mpic` and `pmac_pic_probe_mpic`.

Control flow: `pmac_pic_init` configures OF IRQ parser workarounds, tries MPIC discovery first, and falls back to old-style PIC probing on 32-bit. Old-style probing determines the master/slave controller layout from OF nodes, creates a linear irq domain, maps controller registers, disables all interrupts, wires cascade handling for Gatwick/second controllers, and installs `ppc_md.get_irq`. Interrupt dispatch scans enabled event, level, and software-lost bits from high to low controller words, maps hardware IRQs through the domain, and returns Linux IRQs. Masking and unmasking update cached masks under a raw spinlock and retrigger level interrupts that were already asserted.

State and persistence: in-memory bitmaps cache enabled interrupts and lost interrupts; hardware enable/ack/level/event registers hold controller state. Suspend saves primary controller masks in `sleep_save_mask`, disables all but the PMU VIA wake interrupt, and resume restores masks by unmasking saved IRQs.

Dependencies/integration: integrates with Linux irq domains, generic irq chips, MPIC allocation/init, OF IRQ parsing, PMU VIA wake discovery, XMON NMI hooks, PowerMac feature calls for MPIC enable, and machine `ppc_md.get_irq`.

Risks: old PIC code assumes a maximum of 128 interrupts and specific register layouts. `pmac_pic_probe_oldstyle` prints `%pOF` after `of_node_put(master)`, which is only safe if the node lifetime remains valid. Lost-interrupt retriggering uses decrementer kicks and cached bitmaps, so mask races can produce duplicate or delayed handling if ordering changes. BootX missing-phandle workarounds rely on best-effort default controller selection.

Test signals: boot with MPIC and old PIC hardware; single and cascaded controller layouts; edge and level startup behavior; retrigger of asserted level lines; lost-interrupt accounting; OldWorld `AAPL,interrupts` parsing through PCI parent fallback; BootX no-phandle default PIC detection; XMON NMI registration; suspend/resume with PMU VIA wake interrupt.
