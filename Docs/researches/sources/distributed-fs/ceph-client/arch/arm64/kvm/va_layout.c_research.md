<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/va_layout.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/va_layout.c

## Purpose
This file computes and patches the non-VHE hypervisor virtual address layout. It chooses a randomized HYP VA tag that avoids the ID map, initializes the HYP physical/virtual offset, applies HYP relocations, and emits alternative instruction sequences for fast kernel-to-HYP VA conversion and Spectre vector branching.

## Important APIs, Types, And Functions
- `kvm_hyp_va_bits()` returns the HYP VA size as the maximum of ID map VA bits and actual kernel VA bits.
- `kvm_compute_layout()` computes `tag_lsb`, `va_mask`, and `tag_val`, optionally randomizing tag bits, then initializes `hyp_physvirt_offset`.
- `kvm_apply_hyp_relocations()` walks `.hyp.reloc` entries and rewrites kernel image VAs to HYP VAs.
- `kvm_update_va_mask()` patches a 5-instruction alternative sequence for `kern_hyp_va()` style translation.
- `kvm_patch_vector_branch()` patches a Spectre V3A vector branch sequence to jump into HYP vectors.
- `kvm_get_kimage_voffset()` and `kvm_compute_final_ctr_el0()` patch immediate constants with `kimage_voffset` and sanitized `CTR_EL0`.

## Control Flow
Early init computes layout from the physical ID map address and linear-map DRAM span. The low bits remain the kernel linear VA, while higher tag bits select the HYP region opposite the ID map and may include random bits when KASLR is enabled. Relocation application later rewrites listed HYP-only pointers. Alternative patch callbacks decode original registers and generate replacement AArch64 instructions using the instruction encoder helpers.

## State And Persistence Behavior
Static state `tag_lsb`, `tag_val`, and `va_mask` is initialized once during early boot and then used by relocation and patch callbacks. `hyp_physvirt_offset` is written as EL2-owned shared state. Alternative patching persists in kernel text alternatives.

## Dependencies And Integration Points
The file depends on memblock, randomization, arm64 alternatives, instruction generation, KVM MMU symbols, memory layout helpers, and HYP linker symbols. It integrates with the arm64 alternatives framework and KVM HYP initialization.

## Risks And Edge Cases
- HYP VA layout must not collide with the ID map or lose significant linear-map bits.
- The alternative callbacks assert exact instruction counts; mismatches are fatal.
- VHE bypasses HYP VA translation and NOPs the translation sequence.
- Spectre V3A vector patching must preserve vector slot selection with PC bits and skip the expected preamble.
- Relocation entries must point to valid kernel image VA slots; incorrect linker data corrupts HYP-only pointers.

## Test Signals
Boot tests on VHE and non-VHE systems, KASLR enabled/disabled, different VA sizes, and Spectre V3A-affected hardware are important. KVM init failures, HYP relocation faults, or invalid alternative instruction BUGs are strong signals. Guest entry on non-VHE systems validates the patched translation path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/va_layout.c -->
