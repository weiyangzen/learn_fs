# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_host.h

## Purpose
Defines the x86 KVM host architecture contract: vCPU and VM architectural state, MMU roles, paravirtual clock state, APIC and interrupt acceleration state, Hyper-V/Xen emulation state, PMU/MTRR/MCE state, request bits, statistics, and the static-call operation table implemented by VMX and SVM. It is the central include consumed by x86 KVM core code and vendor backends.

## Important APIs, Types, And Functions
Major exported types include `struct kvm_vcpu_arch`, `struct kvm_arch`, `struct kvm_mmu`, `union kvm_mmu_page_role`, `union kvm_cpu_role`, `struct kvm_pmu`, `struct kvm_pmc`, `struct kvm_x86_ops`, `struct kvm_x86_nested_ops`, `struct kvm_lapic_irq`, and Hyper-V/Xen substructures. Important request and policy macros include `KVM_REQ_*`, `CR0_RESERVED_BITS`, `CR4_RESERVED_BITS`, `PFERR_*`, `KVM_X86_VALID_QUIRKS`, and APICv inhibit reasons. Function declarations cover MMU creation, root freeing, page faults, CR/MSR/register access, exception/NMI injection, emulation, APICv updates, async page fault delivery, TSC scaling, user-return MSRs, and KVM vendor init/exit. `kvm_x86_call()` and `kvm_pmu_call()` route common code through static calls declared via `asm/kvm-x86-ops.h`.

## Control Flow
The header itself is declarative, but it shapes runtime flow. KVM common x86 code queues `KVM_REQ_*` bits, caches dirty registers in `regs_dirty`, dispatches hardware-specific operations through `kvm_x86_ops`, and routes nested virtualization through `nested_ops`. MMU fault handling uses `struct kvm_mmu` callbacks, role unions, root caches, and memory caches. Entry/exit paths use vCPU arch state for interrupt/NMI/SMI injection, emulation completion, MSR interception, TSC offsets, APICv state, and protected guest hooks. VM-scope paths use `struct kvm_arch` locks, memslot metadata, TDP/MMU root lists, clock state, and filters.

## State And Persistence
State is in-memory and scoped to KVM VMs and vCPUs. Persistent-in-runtime fields include guest registers, control registers, FPU state, CPUID capabilities, MSR values, PMU counters and perf events, APIC maps, MTRRs, machine-check banks, async page fault queues, paravirtual time caches, Hyper-V SynIC timers and TLB flush FIFOs, Xen runstate/evtchn caches, MMU roots, rmap/lpage/write-track metadata, and dirty-log CPU state. No filesystem persistence is defined; userspace migration depends on matching this state through KVM ioctls and nested state APIs.

## Dependencies And Integration Points
Depends on Linux KVM core types, mmu notifiers, perf, pvclock, irqbypass, vhost tasks, x86 APIC/debug/MSR/MTRR/descriptor headers, Hyper-V HVDK, page tracking, and vendor implementation files. Integration points include QEMU/KVM ABI structs, VMX/SVM backends, x86 emulator, LAPIC/IOAPIC/PIT, gmem/private memory, TDX/SEV hooks, Hyper-V and Xen emulation, host perf events, user-return MSRs, and trace/error paths.

## Risks And Edge Cases
Risk concentrates in ABI-sensitive struct fields, request bit numbering, role bit packing, APIC ID/vCPU ID sizing, SMM address spaces, private-memory restrictions, TDP MMU root lifetime, APICv inhibit synchronization, nested run pending state, MSR filters, PMU event filtering, Hyper-V TSC page status, and emulation failure behavior. Changing masks such as `PFERR_SYNTHETIC_MASK`, `KVM_CLOCK_VALID_FLAGS`, or reserved CR bits can alter guest-visible behavior. Static-call table changes must remain synchronized with `kvm-x86-ops.h` and vendor implementations.

## Test Signals
Signals include x86 KVM selftests for CPUID/MSR state, nested VMX/SVM, MMU roles, dirty logging, private memory, APICv/AVIC, Hyper-V and Xen features, SMM, TSC scaling, and emulation failures. Build coverage must include VMX, SVM, 32-bit conditionals, KVM disabled, Hyper-V, Xen, SMM, IOAPIC, external write tracking, and protected guest configs.
