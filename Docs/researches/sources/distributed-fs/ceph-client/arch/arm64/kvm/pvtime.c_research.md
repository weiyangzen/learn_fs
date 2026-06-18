# sources/distributed-fs/ceph-client/arch/arm64/kvm/pvtime.c

Purpose: implements arm64 KVM paravirtual stolen-time support. It lets userspace configure a guest physical address for the stolen-time structure, initializes the structure, answers SMCCC PV feature queries, and updates the guest-visible stolen-time counter from host scheduler run-delay accounting.

Important APIs and functions: `kvm_update_stolen_time()` updates the guest memory field. `kvm_hypercall_pv_features()` reports PV time feature availability to the guest. `kvm_init_stolen_time()` zeros and arms the guest structure. `kvm_arm_pvtime_supported()` checks `sched_info_on()`. `kvm_arm_pvtime_set_attr()`, `kvm_arm_pvtime_get_attr()`, and `kvm_arm_pvtime_has_attr()` implement the `KVM_ARM_VCPU_PVTIME_IPA` device attribute.

Control flow: userspace sets the stolen-time IPA through the vCPU device attribute. The setter verifies sched info support, attr ID, user copy, 64-byte alignment, one-shot configuration, and that the target GFN resolves to a valid memslot under SRCU. Initialization records current `current->sched_info.run_delay`, zeros the guest `pvclock_vcpu_stolen_time` structure, and returns the base. Runtime updates read the existing little-endian stolen-time value at `base + offsetof(stolen_time)`, compute the delta in current task run delay since the last update, store the new `last_steal`, and write the accumulated value back to guest memory.

State and persistence: per-vCPU state is `vcpu->arch.steal.base` and `last_steal`. Guest memory persists the ABI structure and accumulated stolen-time value in little-endian format. `INVALID_GPA` disables the feature. No global state is owned by this file.

Dependencies and integration: depends on scheduler `sched_info`, ARM SMCCC PV time function IDs, KVM guest memory access helpers, SRCU, memslot lookup, and the `pvclock-abi.h` layout. It integrates with hypercall handling and vCPU run/load paths that call update/init helpers.

Risks: the configured IPA is validated only at setup; later memslot changes or invalidation rely on normal KVM memory access failure handling. Stolen-time accumulation is tied to the host task's `run_delay`, so update frequency affects when the guest observes increments. Endianness is explicitly little-endian per ABI and must not follow guest CPU endianness. One-shot IPA configuration prevents accidental relocation but means userspace must set it correctly before use.

Test signals: tests should cover unsupported sched-info systems, unaligned IPA rejection, invalid memslot rejection, duplicate set returning `-EEXIST`, get/has attr behavior, feature hypercall success only after base is configured, zero initialization, and monotonic stolen-time accumulation after host scheduling delays.
