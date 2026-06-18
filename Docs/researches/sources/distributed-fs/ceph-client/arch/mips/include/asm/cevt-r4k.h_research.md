<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cevt-r4k.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cevt-r4k.h

**Purpose:** Declares common CP0 Count/Compare clock event support.

**Important APIs/types/functions:** Declares per-CPU `mips_clockevent_device`, `mips_event_handler`, `c0_compare_int_usable`, `c0_compare_interrupt`, and global `cp0_timer_irq_installed`.

**Control flow:** Timer setup installs compare IRQ and clockevent handlers using these declarations.

**State, dependencies, integration:** Integrates MIPS R4K-style CP0 timer with Linux clockevents and interrupts.

**Risks and test signals:** Incorrect compare interrupt usability causes lost ticks. Test timer interrupt install, per-CPU clockevent registration, and CPUs without usable compare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cevt-r4k.h -->
