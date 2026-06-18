<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-sh03/mach/io.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-sh03/mach/io.h

Purpose: defines SH03 external interrupt line priorities.

Important APIs/types/functions: `IRL0_IRQ`..`IRL3_IRQ` and matching priority macros.

Control flow: board IRQ setup consumes these constants to configure external interrupt routing.

State and persistence: state is interrupt controller priority programming performed elsewhere.

Dependencies/integration: integrates with SH03 machine vector and irq setup.

Risks: priority mismatch can starve or invert external device interrupts.

Test signals: verify external IRQ delivery and priority masking on SH03.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-sh03/mach/io.h -->
