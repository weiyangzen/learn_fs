<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7269.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7269.c

Purpose: registers SH7269 pinmux resources.

Important APIs/types/functions: `plat_pinmux_setup()` with SH7269 PFC resource data.

Control flow: hands subtype resources to generic PFC registration.

State and persistence: state is pin configuration managed after platform-device probe.

Dependencies/integration: integrates SH7269 SCIF/CMT/USB/ADC pinmux with platform bus.

Risks: wrong resource base/size makes GPIO or alternate functions unavailable.

Test signals: boot SH7269 and test serial, GPIO, and selected peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7269.c -->
