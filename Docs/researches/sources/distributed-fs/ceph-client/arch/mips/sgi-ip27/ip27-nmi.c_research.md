# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-nmi.c

Purpose: IP27 NMI registration and crash dump support. It installs per-slice NMI callbacks and prints firmware-saved CPU register frames and HUB IRQ state for all nodes.

Important APIs and control flow: `install_cpu_nmi_handler()` writes the NMI magic and callback address into the per-node/slice NMI area if firmware has not already done so. `nmi_cpu_eframe_save()` formats saved GPRs, EPC, ErrorEPC, status, cause, BadVA, cache error, and NMI status. `nmi_dump_hub_irq()` prints per-slice mask and pending registers. `nmi_dump()` serializes through `nmi_lock`, waits for participating CPUs when real NMI signaling is disabled, saves all frames, and resets the local HUB port.

State, persistence, and integration: state includes NMI memory areas, an arch spinlock, and optional atomic participation count. Dependencies include SN NMI layout, online node map, HUB registers, and per-CPU slice mappings. Risks include disabled `REAL_NMI_SIGNAL` alternate code, potential indefinite wait for CPUs, and final local reset after dumping. Test signals are NMI handler installation, emergency register dumps on NMI, and system reset after dump.
