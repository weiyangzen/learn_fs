# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmx.c lines 8867-8879

## Scope

This chunk is the final success and failure tail of `vmx_init()`, the Intel VMX vendor module initializer for x86 KVM. The exact covered lines initialize per-CPU VMX lists and posted-interrupt state for every possible CPU, run the nested-VMX VMCS12 layout sanity check, return success, and define the only local unwind label for failure after common KVM vendor initialization.

The surrounding `vmx_init()` sequence is important context: it first verifies VMX support, initializes Hyper-V enlightened VMCS configuration, parses VMCS hardware capabilities, calls `kvm_x86_vendor_init(&vt_init_ops)`, and then sets up the L1D flush mitigation. Lines 8867-8879 execute only after those earlier global/vendor setup stages have succeeded.

## Purpose

The successful path prepares per-CPU VMX bookkeeping that later runtime paths assume is already initialized:

- `INIT_LIST_HEAD(&per_cpu(loaded_vmcss_on_cpu, cpu))` creates an empty list head for each possible CPU. This list tracks every VMCS currently loaded on that CPU.
- `pi_init_cpu(cpu)` initializes posted-interrupt wakeup list state and its per-CPU lock for the same CPU.
- `vmx_check_vmcs12_offsets()` asserts that KVM's nested-VMX `struct vmcs12` ABI layout still matches the fixed offsets exposed to L1 guests and userspace migration state.

The failure label handles errors from `vmx_setup_l1d_flush()` after `kvm_x86_vendor_init()` has already registered the vendor module and allocated common KVM resources. In that case, `kvm_x86_vendor_exit()` unwinds common x86 KVM state before `vmx_init()` returns the original error.

## Important APIs, Types, And Functions

`vmx_init()` is declared `int __init`, so this path runs during module/load initialization and its code may be discarded after init. It returns `0` on successful registration of VMX support or a negative errno on failure.

`for_each_possible_cpu(cpu)` iterates all CPUs that may ever be present, not just the CPUs online at module load time. That choice is deliberate because hotplugged CPUs need valid per-CPU list heads and posted-interrupt locks before VMX CPU-online paths or vCPU migration can use them.

`loaded_vmcss_on_cpu` is a `DEFINE_PER_CPU(struct list_head, loaded_vmcss_on_cpu)` in `vmx.c`. It backs several VMCS lifecycle paths:

- `vmx_vcpu_load_vmcs()` adds a vCPU's `loaded_vmcs->loaded_vmcss_on_cpu_link` to the destination CPU list after clearing it from any prior CPU.
- `vmx_emergency_disable_virtualization_cpu()` walks the local CPU list and clears all loaded VMCSs during emergency virtualization shutdown.
- `vmclear_local_loaded_vmcss()` walks the local CPU list during normal CPU virtualization disable and calls `__loaded_vmcs_clear()` for every entry.

`pi_init_cpu(int cpu)` is defined in `vmx/posted_intr.c`. It initializes `wakeup_vcpus_on_cpu` with `INIT_LIST_HEAD()` and initializes `wakeup_vcpus_on_cpu_lock` with `raw_spin_lock_init()`. That state is used by posted-interrupt scheduling paths such as `vmx_vcpu_pi_put()`, `vmx_vcpu_pi_load()`, and `pi_wakeup_handler()`.

`vmx_check_vmcs12_offsets()` is a static inline helper in `vmx/vmcs12.h`. It uses `ASSERT_STRUCT_OFFSET()` through `CHECK_OFFSET()` for fixed fields in `struct vmcs12`. The comments around the helper explain that VMCS12 field offsets must not change for save/restore compatibility, although appending fields or filling gaps is allowed.

`kvm_x86_vendor_exit()` is the common x86 KVM vendor teardown routine. In this error path it undoes the successful `kvm_x86_vendor_init()` call by unregistering perf callbacks, tearing down lapic/timer/notifier state, calling the vendor `hardware_unsetup` hook, destroying user-return MSR state, exiting MMU vendor support, destroying the x86 emulator cache, and clearing the active vendor ops pointer under `vendor_module_lock`.

## Control Flow

The relevant control flow is:

1. Earlier `vmx_init()` checks `kvm_is_vmx_supported()`, initializes eVMCS state, parses `vmcs_config` and `vmx_capability`, then calls `kvm_x86_vendor_init(&vt_init_ops)`.
2. After common vendor initialization succeeds, `vmx_setup_l1d_flush()` configures L1TF-related VM-entry flush behavior. This setup can allocate mitigation pages and can fail, typically with `-ENOMEM`.
3. If the L1D setup fails, control jumps to `err_l1d_flush`, calls `kvm_x86_vendor_exit()`, and returns `r`.
4. If L1D setup succeeds, `for_each_possible_cpu(cpu)` initializes VMCS and posted-interrupt per-CPU state for every possible CPU.
5. `vmx_check_vmcs12_offsets()` runs after per-CPU initialization. This is a sanity/ABI assertion stage, not a runtime capability probe.
6. `vmx_init()` returns `0`, completing VMX vendor module initialization.

There are no additional unwind labels after the per-CPU initialization loop. The operations in the loop are list-head and spinlock/list initialization and do not allocate memory or return errors.

## State And Persistence

The chunk mutates global/per-CPU kernel state that persists for the lifetime of the loaded VMX module:

- `loaded_vmcss_on_cpu[cpu]` starts as an empty linked list for each possible CPU. Runtime vCPU load, CPU hotplug, and emergency disable paths later add/remove `struct loaded_vmcs` entries.
- `wakeup_vcpus_on_cpu[cpu]` and `wakeup_vcpus_on_cpu_lock[cpu]` are initialized by `pi_init_cpu()` and persist as posted-interrupt scheduling infrastructure.
- `struct vmcs12` layout is not changed here, but `vmx_check_vmcs12_offsets()` enforces the persistent nested-state ABI contract compiled into KVM.

No file-backed persistence, userspace-visible object creation, or VM-specific allocation occurs in the covered lines. The persistence concern is kernel ABI/state continuity: initialized per-CPU state must remain valid until module exit, and VMCS12 layout must remain compatible with migration/save-restore users.

## Dependencies And Integration Points

This chunk depends on earlier initialization work in `vmx_init()`:

- `setup_vmcs_config(&vmcs_config, &vmx_capability)` must already have established VMX hardware capabilities.
- `kvm_x86_vendor_init(&vt_init_ops)` must already have installed the VMX vendor hooks into the common x86 KVM layer and run `vt_init_ops.hardware_setup`.
- `vmx_setup_l1d_flush()` must have completed because the per-CPU setup is reached only after mitigation state is ready.

The per-CPU VMCS list integrates with `struct loaded_vmcs` in `vmx/vmcs.h`, especially the `loaded_vmcss_on_cpu_link` member. The list is manipulated with interrupts disabled in migration paths where necessary, and `__loaded_vmcs_clear()` uses memory barriers to coordinate CPU ownership changes against `vmx_vcpu_load_vmcs()`.

The posted-interrupt initialization integrates with APICv and VT-d posted interrupt handling. Even if APICv is dynamically disabled for a VM, the initialized per-CPU wakeup lists and locks are still part of the always-compiled VMX posted-interrupt support and are used when conditions allow posted interrupts.

The VMCS12 offset check integrates with nested virtualization, `KVM_GET_NESTED_STATE`/`KVM_SET_NESTED_STATE` compatibility, and L1-visible `MSR_IA32_VMX_BASIC` revision/size semantics. It is a guardrail for developers changing `struct vmcs12`, not a dynamic hardware feature.

The error path integrates with common KVM x86 module lifecycle rules. Because `kvm_x86_vendor_init()` has a "point of no return" internally after some stages, this chunk avoids adding complex unwind below its own post-L1D setup point and delegates cleanup to `kvm_x86_vendor_exit()`.

## Risks And Edge Cases

The main correctness risk is CPU hotplug coverage. Using online CPUs instead of possible CPUs would leave list heads or posted-interrupt locks uninitialized for CPUs hot-added after module load. This chunk uses `for_each_possible_cpu()`, which matches the later per-CPU access patterns.

`loaded_vmcss_on_cpu` is critical for safe VMCS cleanup. If its list heads are not initialized before a vCPU can be loaded or before CPU teardown/emergency paths can walk them, list corruption or crashes are possible. The covered loop must therefore stay before any successful return from `vmx_init()`.

The posted-interrupt state has locking and IRQ-context constraints. `pi_init_cpu()` initializes a raw spinlock that later code takes with interrupts disabled and sometimes under scheduler interactions. Missing or late initialization would break wakeup-vector handling for blocking vCPUs with posted interrupts.

`vmx_check_vmcs12_offsets()` protects nested VMX ABI compatibility. A failed offset assertion is a build/development signal that a VMCS12 layout change would break save/restore compatibility. Removing or bypassing this check could allow subtle live migration or nested-state restore corruption.

The `err_l1d_flush` label only covers failures after common vendor init and before per-CPU no-fail initialization. If a new fallible operation is added after the per-CPU loop, it must be audited for any additional cleanup requirements. The current loop does not need cleanup because reinitializing empty list heads and locks during failed module init has no external allocation to release.

The L1D flush setup failure path is security-sensitive. If mitigation setup fails, the module must not continue with partially configured L1TF mitigation state. Returning through `kvm_x86_vendor_exit()` preserves the invariant that VMX is not registered when required mitigation resources could not be set up.

## Test Signals

Useful validation signals for this chunk include:

- Building KVM with VMX enabled, which catches `vmx_check_vmcs12_offsets()` layout assertions and declaration mismatches for `pi_init_cpu()`.
- Loading `kvm-intel` on VMX-capable hardware and verifying successful module init reaches the `return 0` path.
- Fault-injection or constrained-memory testing around `vmx_setup_l1d_flush()` to confirm failure returns unwind through `kvm_x86_vendor_exit()` and do not leave VMX registered.
- CPU hotplug tests with KVM loaded, exercising CPUs that were possible but not online at module load, to verify per-CPU VMCS and posted-interrupt state was initialized early enough.
- vCPU migration and CPU offline tests that force `vmx_vcpu_load_vmcs()`, `vmclear_local_loaded_vmcss()`, and `vmx_emergency_disable_virtualization_cpu()` to manipulate `loaded_vmcss_on_cpu`.
- APICv/posted-interrupt tests with blocking vCPUs and assigned/bypass interrupts, validating that `wakeup_vcpus_on_cpu` and its lock are usable on all possible CPUs.
- Nested VMX state migration tests, especially `KVM_GET_NESTED_STATE`/`KVM_SET_NESTED_STATE`, to detect any VMCS12 layout drift not already caught at build time.
