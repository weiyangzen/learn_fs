<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/ipr.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/ipr.c

Purpose: implements priority-register based IRQ chips.

Important APIs/types/functions: `register_ipr_controller()`, `enable_ipr_irq()`, `disable_ipr_irq()`.

Control flow: controller registration allocates descriptors, installs a level irq_chip, stores per-IRQ IPR data, disables each IRQ, and later mask/unmask writes 4-bit priorities into IPR registers.

State and persistence: state is per-IRQ `ipr_data`, irq_desc chip data, and hardware IPR register fields.

Dependencies/integration: used by many SH platform setup files that declare `ipr_desc`/intc data.

Risks: bad shifts or offsets silently mask wrong interrupt sources; BUG_ON catches invalid descriptor tables only at boot.

Test signals: boot platforms with each IPR table and verify device interrupt enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/ipr.c -->
