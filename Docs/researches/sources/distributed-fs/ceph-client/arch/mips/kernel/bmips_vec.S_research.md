<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/bmips_vec.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/bmips_vec.S

### Purpose
`bmips_vec.S` implements Broadcom BMIPS reset, NMI, re-entry, warm restart, secondary CPU startup, and XKS01 segment-extension vectors.

### Important APIs, Types, And Functions
Important symbols are `bmips_smp_movevec`, `bmips_reset_nmi_vec`, `bmips_smp_entry`, `bmips_secondary_reentry`, `bmips_reset_nmi_vec_end`, `bmips_smp_int_vec`, `bmips_smp_int_vec_end`, and `bmips_enable_xks01`.

### Control Flow
The move vector relocates CPU1 from the IV vector to the warm restart vector on BMIPS4350-style systems. The reset/NMI vector distinguishes NMI from soft reset, saves state for real NMI, clears status bits, and jumps to `nmi_handler`. SMP reset paths configure CP0 status/config, initialize local I-cache or EBase as needed, enable XKS01, build wired TLB state, load boot stack/global pointer, and jump to `start_secondary`.

### State, Persistence, And Dependencies
State includes CP0 Status, Cause, Config, EBase, Broadcom CP0 register 22 selectors, warm restart vectors copied to fixed addresses, boot stack/global pointer globals, and wired TLB setup.

### Integration Points
BMIPS SMP platform code copies and targets these vectors. It calls `bmips_5xxx_init`, `plat_wired_tlb_setup`, `nmi_handler`, and `start_secondary`.

### Risks
The vector is copied to fixed exception addresses and runs with minimal stack/translation guarantees. PRID-based paths must distinguish BMIPS4350/4380/5000/5200 accurately. Any wrong cacheability or EBase programming can strand secondary CPUs.

### Test Signals
Test CPU1 first boot, hotplug re-entry, NMI handling, BMIPS5200 warm boot, XKS01-enabled high-memory access, and vector copy size/end labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/bmips_vec.S -->
