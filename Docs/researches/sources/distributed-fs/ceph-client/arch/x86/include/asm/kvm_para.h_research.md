# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_para.h

## Purpose
Provides x86 guest-side KVM paravirtualization helpers, hypercall wrappers, KVM clock hooks, async page fault handling, and optional paravirtual spinlock initialization.

## Important APIs, Types, And Functions
Defines `KVM_HYPERCALL` using `ALTERNATIVE("vmcall", "vmmcall", X86_FEATURE_VMMCALL)`, wrappers `kvm_hypercall0()` through `kvm_hypercall4()`, and `kvm_sev_hypercall3()`. Guest hooks include `kvmclock_init()`, `kvmclock_disable()`, `kvm_para_available()`, `kvm_arch_para_features()`, `kvm_arch_para_hints()`, `kvm_async_pf_task_wait_schedule()`, `kvm_read_and_reset_apf_flags()`, `kvm_handle_async_pf()`, and `kvm_spinlock_init()`. TDX guests route hypercalls through `tdx_kvm_hypercall()`.

## Control Flow
Guests place the hypercall number in RAX and up to four arguments in RBX, RCX, RDX, and RSI. If the CPU advertises TDX guest mode, wrappers call the TDX-specific hypercall ABI; otherwise inline assembly emits the patched `vmcall`/`vmmcall` instruction. Async page fault handling is gated by the `kvm_async_pf_enabled` static key so the common path returns false when disabled.

## State And Persistence
The header owns no durable state. It exposes static-key-gated APF state and guest clock initialization hooks implemented elsewhere. Hypercall effects depend on host KVM and guest per-CPU state.

## Dependencies And Integration Points
Depends on x86 processor features, alternatives, interrupt regs, UAPI KVM paravirt definitions, and TDX support. It integrates with KVM guest clocksource code, async page fault exception handling, paravirt spinlocks, SEV/TDX confidential guest paths, and host KVM hypercall emulation.

## Risks And Edge Cases
Register constraints are ABI-critical. TDX and SEV paths must not issue unsupported raw hypercall instructions. Disabled `CONFIG_KVM_GUEST` stubs must be side-effect-free. Async page fault handling must remain cheap when the static key is false.

## Test Signals
Boot KVM guests with KVM clock, async page faults, PV spinlocks, SEV, and TDX. Selftests should verify hypercall argument passing and fallback stubs under non-KVM builds.
