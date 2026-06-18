<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/iss4xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/iss4xx.c

Purpose: supports the IBM ISS 4xx simulator platform, including OF device probing, UIC or MPIC interrupt-controller selection, optional 47x SMP spin-table startup, and reset/progress hooks.

Important APIs/types/functions: `iss4xx_device_probe()` registers PLB/OPB/EBC devices and RTC; `iss4xx_init_irq()` discovers the top-level interrupt controller and initializes UIC or MPIC; SMP helpers `smp_iss4xx_setup_cpu()` and `smp_iss4xx_kick_cpu()` program `cpu-release-addr` spin tables; `iss4xx_setup_arch()` installs SMP ops when appropriate; `define_machine(iss4xx)` binds `ibm,iss-4xx`.

Control flow: interrupt init scans interrupt-controller nodes without an `interrupts` property to find the root. If compatible with `ibm,uic`, it initializes UIC and sets `ppc_md.get_irq`; if compatible with `chrp,open-pic`, it allocates/initializes MPIC. For 47x SMP builds, CPU kick writes CPU number and secondary entry physical address into the spin table.

State and persistence: persistent effects are platform devices, RTC, interrupt controller state, `ppc_md.get_irq`, and optional global `smp_ops`. No local heap state is retained except MPIC/UIC allocations in those subsystems.

Dependencies and integration: depends on OF CPU and interrupt nodes, `uic.c`, MPIC, `start_secondary_47x`, MMU feature detection, generic SMP timebase helpers, and PPC4xx reset.

Risks and test signals: missing or unrecognized top-level interrupt controller panics; spin-table mapping assumes linear mapping and valid `cpu-release-addr`; `of_node_put()` is not visible after the root interrupt scan. Test ISS DT variants with UIC and MPIC, SMP secondary start, RTC instantiation, and simulator reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/iss4xx.c -->
