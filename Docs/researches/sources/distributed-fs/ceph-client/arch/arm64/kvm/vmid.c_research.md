# sources/distributed-fs/ceph-client/arch/arm64/kvm/vmid.c

Purpose: implements KVM VMID allocation for ARM64 stage-2 address spaces, based on the kernel ASID rollover algorithm but tuned for less frequent VMID exhaustion.

Important APIs/types/functions: `kvm_arm_vmid_bits`, `vmid_generation`, `vmid_map`, per-CPU `active_vmids` and `reserved_vmids`, `flush_context`, `check_update_reserved_vmid`, `new_vmid`, `kvm_arm_vmid_clear_active`, `kvm_arm_vmid_update`, `kvm_arm_vmid_alloc_init`, and `kvm_arm_vmid_alloc_free`.

Control flow: `kvm_arm_vmid_update` fast-paths when the VMID already matches the current generation and the current CPU has a nonzero active VMID slot. Otherwise it takes `cpu_vmid_lock`, allocates or refreshes a VMID, and installs it into this CPU's active slot. `new_vmid` first tries to preserve a still-reserved old VMID in the new generation, then reuses the old index if free, then scans for a free index. Exhaustion increments the generation, rebuilds the bitmap from active/reserved VMIDs, and broadcasts `__kvm_flush_vm_context` through hyp code.

State and persistence: allocation state is process-local kernel memory: a generation counter, bitmap, and per-CPU active/reserved slots. VMID zero is reserved, and `VMID_ACTIVE_INVALID` marks schedule-out state so rollover does not preserve VMIDs needlessly. No disk persistence exists.

Dependencies/integration: depends on KVM hyp calls, ARM64 VMID width discovery through `kvm_get_vmid_bits`, per-CPU atomics, raw spinlocks, and the vCPU scheduling path that calls clear/update around guest execution.

Risks: rollover correctness relies on atomic ordering between per-CPU active slots and the global lock. VMID space must exceed possible CPUs; otherwise post-rollover allocation can fail. Broadcast TLB plus I-cache invalidation is heavier than ASID's deferred per-CPU flush but avoids stale stage-2 translations across VMs.

Test signals: VMID reuse without rollover, rollover with active and scheduled-out VMs, concurrent update while generation changes, VMID zero never allocated, warnings when VMID count is too small, and hyp flush invocation on exhaustion.
