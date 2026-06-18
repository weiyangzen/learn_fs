<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/setup-sh7619.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/setup-sh7619.c

Purpose: declares SH7619 interrupt table and core platform devices.

Important APIs/types/functions: INTC vectors/priorities, SCIF0-2, Ethernet, CMT resources, `sh7619_devices_setup()`, `plat_irq_setup()`, `plat_early_device_setup()`.

Control flow: arch initcall registers devices; IRQ setup registers the INTC descriptor; early setup enables CMT clock and adds early console/timer devices.

State and persistence: state is platform-device registry, INTC programming, and STBCR3 clock bit.

Dependencies/integration: integrates serial, sh_eth, sh-cmt, INTC, and early platform infrastructure.

Risks: wrong vector/resource addresses break console, timer, or Ethernet; early clock gating is critical.

Test signals: boot SH7619 with console/timer/network interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/setup-sh7619.c -->
