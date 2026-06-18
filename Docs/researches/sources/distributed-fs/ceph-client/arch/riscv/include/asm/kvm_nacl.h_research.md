<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_nacl.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_nacl.h

## Purpose
Declares KVM nested acceleration shared-memory state, static-key capabilities, SBI NACL switching, and HFENCE synchronization helpers.

## Important APIs, Types, And Functions
types `kvm_vcpu_arch`, `kvm_riscv_nacl`; functions/prototypes `__kvm_riscv_nacl_hfence`, `__kvm_riscv_nacl_switch_to`, `kvm_riscv_nacl_enable`, `kvm_riscv_nacl_disable`, `kvm_riscv_nacl_exit`, `kvm_riscv_nacl_init`; macros/constants `__KVM_NACL_H`, `kvm_riscv_nacl_available()`, `kvm_riscv_nacl_sync_csr_available()`, `kvm_riscv_nacl_sync_hfence_available()`, `kvm_riscv_nacl_sync_sret_available()`, `kvm_riscv_nacl_autoswap_csr_available()`, `lelong_to_cpu(__x) le32_to_cpu(__x)`, `cpu_to_lelong(__x) cpu_to_le32(__x)`, `lelong_to_cpu(__x) le64_to_cpu(__x)`, `cpu_to_lelong(__x) cpu_to_le64(__x)`, `nacl_shmem()`, `nacl_scratch_read_long(__shmem, __offset)`, `nacl_scratch_write_long(__shmem, __offset, __val)`, `nacl_scratch_write_longs(__shmem, __offset, __array, __count)`, plus 20 more.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Special attention: NACL helpers build little-endian shared-memory records and SBI calls for synchronized CSR, HFENCE, SRET, autoswap, and guest/host switch acceleration.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/jump_label.h`, `linux/percpu.h`, `asm/byteorder.h`, `asm/csr.h`, `asm/sbi.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 245 lines, 7700 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_nacl.h -->
