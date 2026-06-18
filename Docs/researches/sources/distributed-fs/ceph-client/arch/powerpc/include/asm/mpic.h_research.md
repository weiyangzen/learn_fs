# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpic.h

Purpose: defines the OpenPIC/MPIC register map, controller instance state, flags, and public APIs for PowerPC interrupt-controller initialization, masking, EOI, IPI, timer, MSI, and machine-check interrupt handling.

Important APIs/types/functions: register macros cover global, timer, per-CPU, per-source, Freescale, and TSI108 variants. `enum mpic_reg_type`, `struct mpic_reg_bank`, `struct mpic_irq_save`, and `struct mpic` model access type, mapped register banks, saved IRQ state, irq domains/chips, ISUs, vectors, protected sources, MSI bitmap, shadows, and PM save data. APIs include `mpic_alloc`, `mpic_assign_isu`, `mpic_init`, priority setters, CPU setup/teardown, IPI request/send, mask/unmask/EOI, and interrupt fetch helpers.

Control flow: platform code allocates an MPIC object, optionally assigns ISUs, initializes hardware, sets up CPU priority/IPIs, and generic IRQ code calls mask/unmask/end and interrupt fetch routines. SMP paths send IPIs through MPIC dispatch registers.

State and persistence: controller state persists in `struct mpic`, irq domains/chips, mapped MMIO/DCR banks, MSI bitmap, protected-source map, vector arrays, and hardware registers. PM save data persists across suspend.

Dependencies and integration points: depends on Linux IRQ core, DCR, MSI bitmap, device tree, SMP, PCI MSI, PM, and platform-specific weird register sets such as TSI108 and U3 HT fixups.

Risks: register offsets vary by implementation and endianness. Flags such as `MPIC_SECONDARY`, `MPIC_USES_DCR`, `MPIC_FSL`, and `MPIC_ENABLE_COREINT` radically change behavior. Incorrect vector, sense, or destination programming can lose interrupts or route them to wrong CPUs.

Test signals: boot MPIC platforms, verify IRQ domain mapping, external IRQ delivery, IPIs, CPU hotplug setup/teardown, MSI allocation, FSL error interrupts, suspend/resume save/restore, and TSI108/U3 variant coverage where hardware exists.
