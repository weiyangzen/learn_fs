# sources/distributed-fs/ceph-client/arch/riscv/kernel/paravirt.c

Purpose: Implements RISC-V paravirtual steal-time support using the SBI STA extension.

Important APIs/types/functions: Defines `pv_time_init()`, `pv_time_cpu_online()`, `pv_time_cpu_down_prepare()`, `pv_time_steal_clock()`, `sbi_sta_steal_time_set_shmem()`, per-CPU `steal_time`, and the `no-steal-acc` early parameter.

Control flow: Boot checks for SBI STA availability, registers paravirt steal-clock operations, and installs CPU hotplug callbacks. On CPU online it shares a per-CPU steal-time memory region with firmware; on down it disables the shared memory. Runtime clock reads return accumulated stolen time.

State and persistence: Per-CPU aligned `struct sbi_sta_struct` buffers persist while CPUs are online. The `steal_acc` command-line flag controls accumulated mode.

Dependencies and integration points: Depends on SBI STA, paravirt time accounting, CPU hotplug states, and scheduler steal-time reporting.

Risks and test signals: Physical address sharing and hotplug cleanup must match firmware expectations or steal time is wrong. Test under KVM/SBI STA hosts, CPU hotplug, `no-steal-acc`, scheduler accounting, and migration if the hypervisor supports it.
