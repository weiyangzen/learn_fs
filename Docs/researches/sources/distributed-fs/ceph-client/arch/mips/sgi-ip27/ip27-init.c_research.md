# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-init.c

Purpose: main IP27 boot initialization. It registers SMP operations, validates firmware node mode, initializes per-hub/per-CPU state, and starts PROM memory discovery.

Important APIs and control flow: `per_hub_init()` records CPUs on a hub, programs CRB timeout, initializes HUB RTC, copies exception vectors to nonzero nodes, and sets CALIAS size. `per_cpu_init()` masks interrupts, initializes the local hub, logs CPU speed, installs IPIs and NMI handler, and enables HUB pending IRQs. `plat_mem_setup()` registers SMP ops, sets reboot hooks, logs CPU presence, validates N/M mode against config, and sets I/O base. `prom_init()` imports command line and calls `prom_meminit()`.

State, persistence, and integration: state includes `master_nasid`, `sn_cpu_info`, hub CPU masks, HUB timeout/RTC registers, and MIPS I/O resource limits. Dependencies include firmware GDA/KL config, HUB registers, timer, SMP, reset, and memory code. Risks include panic on N/M mismatch, per-hub one-time mask assumptions, and early multi-node exception-vector copying. Test signals are node/CPU logs, successful per-CPU IRQ enablement, and completed `prom_meminit()`.
