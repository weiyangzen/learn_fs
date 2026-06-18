# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vgic-v2-cpuif-proxy.c

## Purpose
This hyp helper emulates selected trapped accesses to the GICv2 virtual CPU interface (`GICV`) directly in EL2. It avoids a full exit for normal 32-bit aligned accesses below the deactivate register while preserving architectural behavior for illegal or unsupported accesses.

## Important APIs, Types, and Functions
- `__vgic_v2_perform_cpuif_access(struct kvm_vcpu *vcpu)` is the sole exported function in the file.
- `__is_be()` determines the guest endianness from AArch32 SPSR or AArch64 SCTLR.
- It uses `struct vgic_dist`, `kvm_vgic_global_state.vcpu_hyp_va`, and `kvm_vcpu_dabt_*()` syndrome helpers.

## Control Flow
The handler reconstructs the fault IPA from `FAR`/`HPFAR`, verifies that it falls within the guest's GICv2 CPU interface window, rejects non-32-bit and unaligned accesses by skipping the instruction and returning `-1`, and leaves deactivate-register accesses to the normal exit path. For accepted accesses it computes the hyp VA of the backing GICV register, byte-swaps when the guest is big-endian, performs `readl_relaxed()` or `writel_relaxed()`, updates the target guest register for reads, skips the instruction, and returns `1`.

## State and Persistence
The persistent state is the real or emulated GICV register state behind `vcpu_hyp_va`; this file does not maintain its own storage. Guest architectural state changes are limited to the destination register for reads and the PC advance.

## Dependencies and Integration Points
It integrates with the hyp data-abort exit path and VGIC global state. It depends on fault-syndrome helpers, `kern_hyp_va()` conversion for `vcpu->kvm`, and the global VGIC CPU interface base configured by the main VGIC code.

## Risks and Edge Cases
Risks include incorrect endian conversion, mishandling illegal access sizes, and accidentally emulating deactivate operations that need full VGIC overflow handling. The function deliberately returns `0` for non-GICV and deactivate accesses so the normal KVM path can handle them.

## Test Signals
Test GICv2 guests with little- and big-endian modes, unaligned and wrong-size MMIO, interrupt acknowledge/priority/EOI register accesses, and deactivate accesses that must still exit. Tracepoints around guest exits should show fewer full exits for valid CPU-interface accesses.
