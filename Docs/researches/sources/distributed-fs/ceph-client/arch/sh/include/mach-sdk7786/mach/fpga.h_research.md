<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-sdk7786/mach/fpga.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-sdk7786/mach/fpga.h

Purpose: provides the SDK7786 FPGA register accessors and bit definitions.

Important APIs/types/functions: SRSTR, SRSTR_MAGIC, INTASR, INTAMR, MODSWR, INTTESTR, SYSSR, NRGPR, NMISR, sdk7786_fpga_init, sdk7786_nmi_init, ioread16, fpga_write_reg, iowrite16.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-sdk7786/mach/fpga.h -->
