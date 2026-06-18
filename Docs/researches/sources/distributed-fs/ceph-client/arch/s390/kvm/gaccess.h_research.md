# sources/distributed-fs/ceph-client/arch/s390/kvm/gaccess.h

## Purpose
Provides the public interface for s390 KVM guest memory access. It exposes address conversion helpers, lowcore accessors, logical/real/absolute read and write helpers, keyed access APIs, range-checking APIs, IPTE locking declarations, and vSIE shadow-fault entry points.

## Important APIs, Types, And Functions
Address helpers are `_kvm_s390_real_to_abs`, `kvm_s390_real_to_abs`, `_kvm_s390_logical_to_effective`, and `kvm_s390_logical_to_effective`. Lowcore helpers are `put_guest_lc`, `write_guest_lc`, and `read_guest_lc`. `enum gacc_mode` distinguishes fetch, store, and instruction fetch. Main APIs include `guest_translate_address_with_key`, `check_gva_range`, `check_gpa_range`, `access_guest_abs_with_key`, `access_guest_with_key`, `access_guest_real`, `cmpxchg_guest_abs_with_key`, `write_guest_with_key`, `read_guest_with_key`, `read_guest_instr`, `write_guest_abs`, `read_guest_abs`, `write_guest_real`, and `read_guest_real`. It also declares `ipte_lock`, `ipte_unlock`, `ipte_lock_held`, `kvm_s390_check_low_addr_prot_real`, `union mvpg_pei`, and `gaccess_shadow_fault`.

## Control Flow
Most inline wrappers select a mode and key, then delegate to the implementation in `gaccess.c`. Logical helpers use the vCPU PSW key unless a caller supplies an explicit access key. Instruction fetches force the translation mode needed by the architecture. Lowcore helpers apply the vCPU prefix and call raw KVM guest read/write helpers without key or low-address checks. Real helpers translate the real address through prefixing and then use the real-access implementation.

## State And Persistence
The header does not own state. It documents that many helpers may update `vcpu->arch.pgm` on positive program-interruption returns and that absolute/lowcore raw helpers may partially copy on host errors. The `union mvpg_pei` result carries shadow/MVPG partial-execution metadata such as DAT table address, not-PTE flag, DAT protection, and real-space indicator.

## Dependencies And Integration Points
Depends on KVM host types, uaccess, ptrace, and `kvm-s390.h`. It is included by diagnose, intercept, guest debug, gmap, and instruction-emulation code that needs architecture-correct guest memory access or exception reporting.

## Risks And Edge Cases
Callers must distinguish positive guest program-interruption codes from negative host errors. Raw absolute and lowcore helpers deliberately bypass storage-key and low-address protection and can partially copy. Logical access can allocate temporary GPA arrays and can require the IPTE lock. `put_guest_lc` assumes the destination is in lowcore; using it elsewhere is undefined by the local contract.

## Test Signals
Compile all s390 KVM users and run guest-memory access tests. Important cases are lowcore prefixing, DAT-off real access, logical address truncation, explicit versus PSW access keys, positive exception returns followed by `kvm_s390_inject_prog_cond`, and MVPG/vSIE callers consuming `union mvpg_pei`.
