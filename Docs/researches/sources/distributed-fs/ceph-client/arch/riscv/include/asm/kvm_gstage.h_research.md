<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_gstage.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_gstage.h

## Purpose
Declares KVM guest-stage page-table state, mapping, unmapping, write-protect, and G-stage mode detection.

## Important APIs, Types, And Functions
types `kvm_gstage`, `kvm`, `kvm_gstage_mapping`, `kvm_mmu_memory_cache`, `kvm_riscv_gstage_op`; functions/prototypes `kvm_riscv_gstage_gpa_bits`, `kvm_riscv_gstage_get_leaf`, `kvm_riscv_gstage_set_pte`, `kvm_riscv_gstage_map_page`, `kvm_riscv_gstage_split_huge`, `kvm_riscv_gstage_op_pte`, `kvm_riscv_gstage_unmap_range`, `kvm_riscv_gstage_wp_range`, `kvm_riscv_gstage_mode_detect`, `kvm_riscv_gstage_mode`, `kvm_riscv_gstage_init`, `kvm_riscv_gstage_max_pgd_levels`; macros/constants `__RISCV_KVM_GSTAGE_H_`, `KVM_GSTAGE_FLAGS_LOCAL`, `kvm_riscv_gstage_index_bits`, `kvm_riscv_gstage_pgd_xbits`, `kvm_riscv_gstage_pgd_size`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/kvm_types.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 109 lines, 2854 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_gstage.h -->
