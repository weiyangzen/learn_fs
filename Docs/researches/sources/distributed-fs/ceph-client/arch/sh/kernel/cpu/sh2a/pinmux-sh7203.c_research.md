<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7203.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7203.c

Purpose: registers SH7203 pinmux resources.

Important APIs/types/functions: `plat_pinmux_setup()` with SH7203 PFC resource data.

Control flow: calls generic PFC platform registration for this subtype.

State and persistence: state is later PFC driver register programming.

Dependencies/integration: integrates SH7203 board setup with pinctrl/GPIO.

Risks: wrong resource range prevents serial/peripheral pin muxing.

Test signals: boot SH7203 and verify GPIO and SCIF pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7203.c -->
