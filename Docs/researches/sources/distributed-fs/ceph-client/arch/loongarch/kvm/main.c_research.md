# sources/distributed-fs/ceph-client/arch/loongarch/kvm/main.c

Purpose: owns LoongArch KVM global initialization, virtual CPU ID/VPID management, guest CSR classification, per-CPU VMCS context allocation, hardware enable/disable, and device registration.

Important APIs, types, and functions: globals include `vpid_mask`, `kvm_loongarch_ops`, `gcsr_flag[]`, and per-CPU `vmcs`. Entry points include `get_gcsr_flag()`, `kvm_check_vpid()`, `kvm_init_vmcs()`, `kvm_arch_enable_virtualization_cpu()`, `kvm_arch_disable_virtualization_cpu()`, module init/exit, and internal `kvm_init_gcsr_flag()`, `kvm_update_vpid()`, `kvm_loongarch_env_init()`.

Control flow: environment init allocates per-CPU contexts and world-switch ops, reads GID/VPID width, initializes per-CPU VPID caches, classifies hardware versus software guest CSRs, registers perf callbacks and LoongArch KVM device types. CPU enable programs GCFG/GSTAT/GINTC/GTLBC and flushes TLBs. VPID checks allocate a fresh VPID on CPU migration or version change, flush all TLBs on wrap, clear stale GPA flush requests, and update GSTAT.GID.

State and persistence: persistent module state includes per-CPU `struct kvm_context`, the world-switch operation table, CSR classification flags, and VPID caches. Per-vCPU `arch.vpid` and `cpu` are updated on entry.

Dependencies and integration points: ties together `switch.S` entry points, `vcpu.c` load/run paths, CSR helpers, TLB flushing, perf callbacks, and IPI/EIOINTC/PCH-PIC/DMSINTC device registration.

Risks: CSR classification errors can cause unsupported hardware accesses or missed software emulation. VPID wrap/migration logic is central to TLB correctness. Environment init error paths after partial device registration should be watched.

Test signals: module load/unload, per-CPU hardware enabling around CPU hotplug/suspend, guest TLB isolation, VPID tracepoints, and KVM device type availability.
