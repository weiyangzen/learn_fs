<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rcpm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rcpm.c

Purpose: QorIQ Run Control/Power Management support for CPU idle/offline, platform sleep, IP block power control, interrupt masking, and time-base freeze across RCPM v1/v2 hardware.

Important APIs/types/functions: init `fsl_rcpm_init()`, ops tables `qoriq_rcpm_v1_ops` and `qoriq_rcpm_v2_ops`, IRQ mask/unmask helpers, CPU enter/exit/up/die helpers, platform sleep helpers, `rcpm_*_set_ip_power()`, `rcpm_*_freeze_time_base()`, `rcpm_get_pm_modes()`, and `qoriq_pm_ops` assignment.

Control flow: init finds a compatible RCPM node, maps registers, sets supported modes to sleep, and publishes the matching v1/v2 ops table. CPU PM callbacks set or clear per-CPU/thread PH10/PH15/PH20/PH30 request/clear registers. Offline for v2 may disable one thread or place a whole core into PH20 depending on thread sibling state. Platform sleep sets the sleep/LPM20 request bit and polls for status clear after resume. IRQ callbacks mask/unmask interrupt classes per hardware CPU. Time-base freeze snapshots enabled bits, clears them, then restores them on unfreeze.

State and persistence: global v1/v2 register pointers alias the same mapped base, `fsl_supported_pm_modes`, and a static time-base mask in `rcpm_common_freeze_time_base()`. Hardware PM request/mask/power/time-base registers persist until changed.

Dependencies and integration points: depends on OF matching, QorIQ GUTS register definitions, `asm/fsl_pm.h`, CPU threading helpers, Book3E thread stop on PPC64, and platform PM/CPU hotplug code consuming `qoriq_pm_ops`.

Risks: hard CPU IDs and thread/core indexes differ; wrong mask calculations can affect the wrong CPU or thread. The static time-base mask is shared across v1/v2 calls and assumes serialized freeze/unfreeze. Sleep polling failures return `-ETIMEDOUT`.

Test signals: CPU hotplug/offline on QorIQ, idle state entry/exit, suspend-to-sleep/LPM20, IP power gating, time-base freeze/resume, and interrupt delivery after mask/unmask validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rcpm.c -->
