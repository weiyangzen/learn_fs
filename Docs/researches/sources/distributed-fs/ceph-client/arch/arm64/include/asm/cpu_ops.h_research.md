## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpu_ops.h

Purpose: abstracts platform-specific CPU boot, suspend, and shutdown operations.

Important APIs/types/functions: defines `struct cpu_operations` with `name`, `cpu_init`, `cpu_prepare`, `cpu_boot`, `cpu_postboot`, `cpu_can_disable`, `cpu_disable`, `cpu_die`, `cpu_kill`, and `cpu_suspend`. Declares `init_cpu_ops`, `get_cpu_ops`, and inline `init_bootcpu_ops`.

Control flow: boot code selects operations per CPU, initializes the boot CPU, then uses the table for secondary CPU lifecycle and suspend paths.

State and persistence: the selected `cpu_operations` pointer per CPU is maintained by implementation code; this header only declares the contract.

Dependencies and integration: used by PSCI/spin-table CPU bring-up, hotplug, suspend, and SMP initialization.

Risks: wrong return semantics or missing hooks strand CPUs during hotplug or resume. Test signals are SMP boot, CPU hotplug loops, suspend/resume, PSCI and non-PSCI platform tests.
