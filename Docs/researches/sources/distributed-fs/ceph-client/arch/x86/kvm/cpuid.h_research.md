# sources/distributed-fs/ceph-client/arch/x86/kvm/cpuid.h

## Purpose

`cpuid.h` is the shared interface for x86 KVM CPUID capability management and guest CPUID queries. It declares CPUID ioctl and emulation entry points, exposes global KVM CPU capability storage, and provides hot inline helpers for guest feature checks, physical-address legality, paravirtual feature enforcement, and selected MSR availability.

## Important APIs, Types, And Functions

- `kvm_cpu_caps[]` and `kvm_is_configuring_cpu_caps`.
- Initialization and ioctl declarations: `kvm_initialize_cpu_caps()`, `kvm_finalize_cpu_caps()`, `kvm_dev_ioctl_get_cpuid()`, `kvm_vcpu_ioctl_set_cpuid()`, `kvm_vcpu_ioctl_set_cpuid2()`, `kvm_vcpu_ioctl_get_cpuid2()`.
- Lookup helpers: `kvm_find_cpuid_entry2()`, `kvm_find_cpuid_entry_index()`, `kvm_find_cpuid_entry()`, and `KVM_CPUID_INDEX_NOT_SIGNIFICANT`.
- Runtime query helpers: `kvm_cpuid()`, `guest_cpuid_has()`, `guest_cpu_cap_has()`, `guest_pv_has()`.
- Address helpers: `cpuid_query_maxphyaddr()`, `cpuid_query_maxguestphyaddr()`, `kvm_vcpu_reserved_gpa_bits_raw()`, `kvm_vcpu_is_legal_gpa()`, `kvm_vcpu_is_legal_cr3()`, `page_address_valid()`.
- Capability mutators/readers: `cpuid_entry_override()`, `kvm_cpu_cap_set()`, `kvm_cpu_cap_clear()`, `kvm_cpu_cap_has()`, `guest_cpu_cap_set()`, `guest_cpu_cap_clear()`, `guest_cpu_cap_change()`.

## Control Flow

Capability initialization code mutates `kvm_cpu_caps[]` only while `kvm_is_configuring_cpu_caps` is true, then `kvm_finalize_cpu_caps()` closes the window. CPUID generation uses `cpuid_entry_override()` to copy a KVM capability word into a CPUID register.

Most guest feature checks use `vcpu->arch.cpu_caps` via `guest_cpu_cap_has()`. The explicit raw-CPUID exception is `guest_cpuid_has()` for XSAVES, because KVM may need internal XSAVES handling while still honoring userspace's direct XSS exposure policy.

Physical-address helpers use cached `maxphyaddr` and `reserved_gpa_bits`; CR3 validation strips LAM tag bits when the guest has LAM.

## State And Persistence

The header defines access to state held by `cpuid.c` and `struct kvm_vcpu_arch`: CPUID entries, cached guest capabilities, paravirtual CPUID enforcement, MAXPHYADDR, reserved GPA bits, and MSR CPUID-faulting fields. It distinguishes raw userspace CPUID from KVM's derived operational feature model.

## Dependencies And Integration Points

The header depends on `reverse_cpuid.h`, x86 CPU helpers, and KVM paravirtual UAPI definitions. It is consumed by KVM x86 core, MMU, emulator, PMU, MSR, and vendor code.

## Risks And Maintenance Notes

- `KVM_CPUID_INDEX_NOT_SIGNIFICANT` must be treated as a `u64` sentinel.
- Dynamic APIC, OSXSAVE, and OSPKE bits are intentionally blocked in `guest_cpu_cap_has()`.
- Expanding `guest_cpuid_has()` beyond XSAVES risks bypassing KVM's cached capability model.
- GPA legality helpers require refreshed derived CPUID state after MAXPHYADDR changes.

## Test Signals

Useful tests include CPUID lookup by significant/non-significant index, XSAVES/XSS exposure behavior, CPUID fault MSR behavior, SPEC_CTRL/PRED_CMD MSR predicates, LAM-tagged CR3 validation, and build-time feature mapping assertions.
