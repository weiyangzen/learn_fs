<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/pfc.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/pfc.c

Purpose: registers SH pin-function-controller resources.

Important APIs/types/functions: `plat_pinmux_setup()` weak/default path and `platform_device` resource registration.

Control flow: subtype pinmux files provide resources; setup registers the PFC platform device for the pinctrl driver.

State and persistence: pinmux state is hardware register programming later performed by PFC driver.

Dependencies/integration: integrates CPU subtype pinmux resource tables with platform bus/pinctrl.

Risks: missing or wrong resources prevent GPIO/peripheral muxing while compiling cleanly.

Test signals: boot pinmux subtypes and verify serial/GPIO/peripheral pin states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/pfc.c -->
