# sources/distributed-fs/ceph-client/arch/mips/kvm/vz.c

Purpose: implements the MIPS KVM backend for CPUs with VZ hardware virtualization. It wires KVM's MIPS callback table to VZ-specific CP0 context management, guest interrupt injection, guest timer handling, guest-exit emulation, TLB/GuestID maintenance, vCPU load/put/run paths, and module initialization.

Important APIs/functions: exposes `kvm_mips_callbacks`, `kvm_mips_emulation_init`, `kvm_vz_acquire_htimer`, and `kvm_vz_lose_htimer`; callback methods include `kvm_vz_vcpu_setup`, `kvm_vz_vcpu_load`, `kvm_vz_vcpu_put`, `kvm_vz_vcpu_run`, `kvm_vz_get_one_reg`, `kvm_vz_set_one_reg`, `kvm_trap_vz_handle_guest_exit`, and TLB-miss handlers. The code maintains CP0 config write masks, guest register index lists, MAAR handling, Loongson CPUCFG/Diag special cases, GuestCtl interrupt state, and guest VTLB sizing.

Control flow: initialization checks `cpu_has_vz` and registers the callback table. Per-vCPU setup seeds reset-state CP0 registers and timer frequency. CPU virtualization enable resizes/partitions guest TLB resources, configures GuestCtl0/1/2, GuestID caches, and CPU-specific Octeon/Loongson quirks. On vCPU entry, state is restored, interrupts are delivered, htimer may be acquired, GuestID/TLB state is refreshed, wired entries are loaded, and the low-level run function is invoked. Exits dispatch by guest exception code to GPSI, GSFC, hypercall, guest mode-change, MMIO load/store, coprocessor, and MSA paths.

State and persistence: persistent per-CPU state lives in `last_vcpu`, `last_exec_vcpu`, `cpu_data[].guestid_cache`, and `kvm_vz_guest_vtlb_size`; per-vCPU state includes software CP0 shadow registers, MAAR array, wired TLB backup, guest IDs per CPU, count/timer fields, pending exception bitmaps, and last scheduled/executed CPU. Hardware CP0 guest registers are saved/restored across scheduling and preemption boundaries; no disk persistence exists.

Dependencies and integration: depends on MIPS CP0 helpers, KVM MIPS common code, TLB helpers, hrtimer count emulation, FPU/MSA ownership code, tracepoints, kernel user-copy APIs, and CPU feature flags. It integrates with KVM ioctls through one-reg get/set/copy callbacks and with VM memory through GPA TLB handling and MMIO emulation.

Risks: correctness is highly sensitive to CP0 hazard ordering, guest timer handoff races, GuestID wrap/flushing, CPU feature asymmetry, writable Config masks, MMIO badvaddr GVA-to-GPA conversion, and failure paths that roll back guest PC. Wired TLB allocation uses `GFP_ATOMIC` and may preserve partial state on failure. Mismatched guest VTLB size across CPUs is treated as an error.

Test signals: build `CONFIG_KVM_MIPS_VZ` on supported MIPS variants, boot VZ guests, exercise KVM one-reg get/set ioctls, timer migration/preemption, SMP vCPU migration, MMIO load/store exits, FPU/MSA lazy ownership, GuestID wrap/TLB flush paths, Loongson-specific CPUCFG/Diag exits, and negative tests on CPUs without VZ.
