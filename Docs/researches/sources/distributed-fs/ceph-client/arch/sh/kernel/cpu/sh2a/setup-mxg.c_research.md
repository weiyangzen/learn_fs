<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-mxg.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-mxg.c

Purpose: declares Renesas MX-G interrupt table and platform devices.

Important APIs/types/functions: INTC vectors/priorities/masks, SCIF0 and MTU2 resources, `mxg_devices_setup()`, `plat_irq_setup()`, `plat_early_device_setup()`.

Control flow: arch initcall registers SCIF/MTU2; IRQ setup registers INTC; early setup registers early console/timer devices.

State and persistence: state is platform-device registry and INTC priority/mask registers.

Dependencies/integration: integrates MX-G serial/timer with generic SH INTC and early platform framework.

Risks: empty priority slots and exact vector numbers are hardware contracts.

Test signals: boot MX-G with console/timer interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-mxg.c -->
