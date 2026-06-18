# sources/distributed-fs/ceph-client/include/linux/soc/renesas/rcar-sysc.h

Purpose: This Renesas R-Car header declares CPU power control helpers in the system controller.

Important APIs/types/functions: It declares `rcar_sysc_power_down_cpu(unsigned int cpu)` and `rcar_sysc_power_up_cpu(unsigned int cpu)`.

Control flow: CPU hotplug or suspend code calls these helpers to transition individual CPUs through the R-Car SYSC power controller.

State and persistence: CPU power state is maintained in SYSC registers and affects core availability until powered up again.

Dependencies and integration: Integrates with Renesas R-Car SMP, CPU hotplug, suspend/resume, and power-domain code.

Risks and test signals: Incorrect CPU index or power sequencing can hang SMP bring-up or hotplug. Test CPU offline/online cycles, system suspend, and failure paths for invalid CPUs.
