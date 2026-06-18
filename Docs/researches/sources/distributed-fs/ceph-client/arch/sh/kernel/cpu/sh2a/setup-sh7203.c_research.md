<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7203.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7203.c

Purpose: declares SH7203/SH7263 interrupt table and platform devices.

Important APIs/types/functions: INTC vectors/groups/priorities/masks, conditional SH7263-only vectors, SCIF0-3, timer resources, `sh7203_devices_setup()`, `plat_irq_setup()`, `plat_early_device_setup()`.

Control flow: registers devices by arch initcall, registers INTC at IRQ setup, and exposes early console/timer devices before normal driver probing.

State and persistence: state is platform-device registry, INTC priority/mask registers, and subtype clock-gate bits.

Dependencies/integration: integrates SH7203/SH7263 serial, timers, optional SH7263 devices, and generic SH INTC.

Risks: conditional SH7203 vs SH7263 tables can misassign vectors if config is wrong.

Test signals: boot both subtypes and test SCIF, timers, USB/LCDC/SDHI/RTC where present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7203.c -->
