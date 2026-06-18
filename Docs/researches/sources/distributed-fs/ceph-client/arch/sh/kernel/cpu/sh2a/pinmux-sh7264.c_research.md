<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7264.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7264.c

Purpose: registers SH7264 pinmux resources.

Important APIs/types/functions: `plat_pinmux_setup()` with SH7264 PFC resource data.

Control flow: registers subtype-specific PFC resources for the pinctrl driver.

State and persistence: state is hardware mux configuration owned by PFC driver.

Dependencies/integration: integrates SH7264 peripherals such as SCIF, CMT, SDHI, USB, ADC with pinctrl.

Risks: resource mistakes break peripheral pins without obvious compile errors.

Test signals: boot SH7264 and validate enabled peripheral pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7264.c -->
