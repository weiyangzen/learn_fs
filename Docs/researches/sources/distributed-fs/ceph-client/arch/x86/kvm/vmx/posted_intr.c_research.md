# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/posted_intr.c

## Purpose
Implements VMX posted interrupt lifecycle support, including per-vCPU PI descriptor updates on vCPU load/put, wakeup handling for blocked vCPUs, APICv state restore cleanup, pending interrupt checks, and VT-d interrupt remapping integration.

## Important APIs, Types, And Functions
Public functions are `vmx_vcpu_pi_load()`, `vmx_vcpu_pi_put()`, `pi_wakeup_handler()`, `pi_init_cpu()`, `pi_apicv_pre_state_restore()`, `pi_has_pending_interrupt()`, `vmx_pi_start_bypass()`, and `vmx_pi_update_irte()`. Key internal helpers are `vcpu_to_pi_desc()`, `pi_try_set_control()`, `vmx_can_use_vtd_pi()`, `pi_enable_wakeup_handler()`, and `vmx_needs_pi_wakeup()`. Per-CPU state consists of `wakeup_vcpus_on_cpu` and `wakeup_vcpus_on_cpu_lock`.

## Control Flow
On vCPU load, `vmx_vcpu_pi_load()` refreshes the PI descriptor destination APIC ID, clears suppress-notification, restores the normal posted interrupt vector, removes the vCPU from the previous CPU wake list if it was blocking, and sets ON if PIR is nonempty. On vCPU put, `vmx_vcpu_pi_put()` either installs the wakeup vector and queues the vCPU on a per-CPU wake list when the vCPU is blocking with interrupts allowed, or suppresses notifications to avoid spurious host IRQs. The wakeup interrupt runs `pi_wakeup_handler()`, which scans the local wake list and wakes vCPUs whose PI descriptor ON bit is set. VT-d irqfd updates call `irq_set_vcpu_affinity()` with PI descriptor physical address and vector.

## State And Persistence
The PI descriptor in `vcpu_vt` stores PIR bits, ON/SN flags, notification vector, and destination. `vcpu_vt::pi_wakeup_list` links a blocked vCPU into exactly one per-CPU wake list. Descriptor control updates are atomic via `try_cmpxchg64()` because hardware or other vCPUs can set ON concurrently. The per-CPU wake lists persist for CPU lifetime and are initialized by `pi_init_cpu()`.

## Dependencies And Integration Points
Depends on APICv capability state, local APIC in-kernel mode, VMX/VT common vCPU structures, TDX interrupt allowance checks, irq bypass, irq remapping, and KVM request/wakeup APIs. It integrates with scheduler load/put hooks, posted interrupt vectors, VT-d interrupt remapping, and TDX posted-interrupt delivery, while excluding TDX from IPIV wakeup use.

## Risks
The main risks are CPU migration races, lock ordering between scheduler locks and wakeup locks, lost posted interrupts when switching vectors, and stale PI destination fields after hotplug or migration. The code disables IRQs around per-CPU lock operations to avoid deadlocks with the wakeup interrupt. Incorrect SN/ON ordering could either lose wakeups or cause interrupt storms.

## Test Signals
Relevant signals include APICv and posted-interrupt KVM tests, irqfd passthrough tests, vCPU block/wakeup under migration, CPU hotplug while TD/VMX vCPUs are loaded, and stress with dynamic APICv inhibition. WARNs for SN set before blocking and failures in irq affinity update are important diagnostics.
