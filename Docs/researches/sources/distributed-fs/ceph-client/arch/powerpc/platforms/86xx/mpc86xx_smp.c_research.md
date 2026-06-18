# sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx_smp.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx_smp.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx_smp.c

### Purpose
SMP initialization for 86xx systems. It starts secondary CPUs using board/firmware release mechanisms and plugs MPIC-based IPI operations into the PowerPC SMP core.

### Important APIs, Types, And Functions
Important functions include `smp_86xx_kick_cpu()`, 86xx SMP operation structures, per-CPU setup, and public `mpc86xx_smp_init()`. It depends on MPIC SMP helpers such as `smp_mpic_probe`, `smp_mpic_message_pass`, and `mpic_setup_this_cpu`.

### Control Flow
Board setup calls `mpc86xx_smp_init()`. It installs MPIC SMP callbacks and sets `smp_ops`. CPU kick paths release secondary CPUs and mark them up through generic SMP state.

### State, Persistence, And Dependencies
State includes the `smp_ops_t` instance and CPU bring-up status. No durable persistence. Dependencies include MPIC, OF CPU descriptions, PowerPC SMP core, and interrupt setup from `pic.c`.

### Integration Points
Used by GE and MVME 86xx machine setup to enable secondary CPUs and IPIs.

### Risks
CPU-release assumptions, IPI routing, and per-CPU MPIC setup are boot-critical. Failures usually hang boot or leave CPUs offline.

### Test Signals
Boot SMP 86xx systems, verify secondary CPUs online, IPI delivery, CPU hotplug if available, and interrupt affinity behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx_smp.c -->
