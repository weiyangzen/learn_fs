<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic.c

Purpose: Implements the OpenPIC/MPIC interrupt controller driver for PowerPC, covering MMIO/DCR register access, irqdomain mapping, masking, EOI, IRQ type/affinity, IPIs, timers, cascaded secondary MPICs, Freescale extensions, U3/U4 HyperTransport workarounds, and suspend/resume save/restore.

Important APIs/types/functions: Exports `mpic_subsys`, `mpic_alloc()`, `mpic_assign_isu()`, `mpic_init()`, `mpic_unmask_irq()`, `mpic_mask_irq()`, `mpic_end_irq()`, `mpic_set_irq_type()`, `mpic_set_vector()`, `mpic_set_affinity()`, `mpic_irq_set_priority()`, `mpic_setup_this_cpu()`, `mpic_teardown_this_cpu()`, `mpic_cpu_get_priority()`, `mpic_cpu_set_priority()`, `mpic_get_one_irq()`, `mpic_get_irq()`, `mpic_get_coreint_irq()`, `mpic_get_mcirq()`, `mpic_request_ipis()`, `smp_mpic_message_pass()`, `smp_mpic_probe()`, `smp_mpic_setup_cpu()`, `mpic_reset_core()`, and `fsl_mpic_primary_get_version()`.

Control flow: Allocation finds or takes an OF node, infers flags and physical address, maps global/timer/per-CPU/ISU registers, computes reserved vectors for timers/IPIs/spurious, handles protected sources, resets hardware unless disabled, creates the irqdomain, and sets the default domain for primary MPICs. Initialization programs processor priority, timer vectors, IPI vectors, optional HT/MSI workarounds, source vector/priority/destination registers, spurious vector, passthrough disable, secondary cascade handler, and FSL error interrupt setup. Domain mapping separates IPIs, timer interrupts, error interrupts, protected/out-of-range sources, and normal sources; normal sources are initialized lazily when `MPIC_NO_RESET` is set. Runtime IRQ flow reads INTACK/EPR/MCACK, maps vectors to Linux IRQs, masks/unmasks by toggling VECPRI mask bits with polling, and EOIs through the current CPU EOI register.

State and persistence: Global state includes linked list `mpics`, `mpic_primary`, `mpic_lock`, per-instance register banks, flags, hardware register set, vector reservations, protected bitmap, irqdomain, chip templates, MSI bitmap, HT fixups, ISU geometry, and optional PM save data. Per-CPU priority and destination registers are hardware state. Suspend stores per-source vecpri/destination and resumes them, including HT fixup data.

Dependencies and integration points: Integrates with OF interrupt parsing, irqdomain, generic IRQ chips/handlers, SMP message IPIs, PowerPC `ppc_md.get_irq`, FSL MPIC error interrupt helpers in `mpic.h`, MPIC MSI helpers, syscore PM, PCI HT capability scanning, and DCR/MMIO endian accessors.

Risks: This is central interrupt routing code with subtle hardware variations. Miscomputed vector ranges can collide with IPIs/timers/spurious/error vectors. Mask/unmask loops can time out. U3/U4 HT fixups hard-code config-space behavior and Apple quirks. Several init failure paths intentionally leak mappings/objects. The driver supports only one primary MPIC for many exported helpers.

Test signals: Boot on OpenPIC, Freescale MPIC, secondary cascaded MPIC, and U3/U4 platforms; IRQ type and affinity changes; SMP IPI delivery; timer vector mapping; protected-source rejection; coreint/EPR path on BookE; suspend/resume; MSI allocation; and stress with spurious/protected vectors.

Source read size: 2022 lines, 52309 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic.c -->
