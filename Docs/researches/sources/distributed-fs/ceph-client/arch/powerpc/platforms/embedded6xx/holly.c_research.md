# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/holly.c

Purpose: IBM PPC750GX/CL Holly/Hickory board support using the TSI108 bridge, MPIC, PCI setup, restart path, and machine-check recovery.

Important APIs and control flow: `holly_remap_bridge` reprograms TSI108 processor/PCI LUTs, I/O, config, and memory windows. `holly_init_pci` calls `tsi108_setup_pci` and excludes root bridge device 0 from PCI probing. `holly_init_IRQ` allocates a TSI108 MPIC, assigns ISUs, optionally initializes the PCI interrupt router cascade, and routes MPIC outputs to CPU0. `holly_restart` maps the TSI bridge, sets BOOT routing, loads SRR0/SRR1, and uses `rfi` to jump to firmware. `ppc750_machine_check_exception` uses exception-table fixups to recover PCI config faults.

State, dependencies, and risks: state includes `tsi108_csr_vir_base`, `ppc_md.pci_exclude_device`, MPIC/cascade handlers, and bridge MMIO configuration. Dependencies include TSI108 register helpers, OF `pci`, `pic-router`, and `tsi-bridge` nodes, MPIC, and extable support. Risks are destructive bridge reprogramming, missing OF nodes causing partial IRQ setup, and restart relying on firmware vectors. Test signals are PCI enumeration, TSI108 interrupt routing, recoverable config-space machine checks, and successful firmware restart.
