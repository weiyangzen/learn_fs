# sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/kvm.h

## Purpose
s390 userspace KVM ABI header for tools, covering storage keys, CMMA, memory operations, interrupts, protected virtualization, zPCI, FLIC, VM attributes, CPU model/crypto/migration, register structs, guest debug, sync regs, and one-reg IDs.

## Important APIs, Types, and Functions
Important types include `kvm_s390_skeys`, `kvm_s390_cmma_log`, `kvm_s390_mem_op`, `kvm_s390_psw`, interrupt info unions, PV command/info structs, `kvm_s390_zpci_op`, adapter/AIS request structs, CPU model feature/subfunction structs, `kvm_regs`, `kvm_sregs`, `kvm_fpu`, debug structs, and the large `kvm_sync_regs` block. Enums define PV command groups and info IDs.

## Control Flow, State, and Persistence
This is ioctl ABI. Userspace passes structured payloads and flags; KVM persists guest CPU, memory, interrupt, PV, and device state. `KVM_SYNC_*` bits select which fields in `kvm_sync_regs` are valid.

## Dependencies and Integration Points
Depends on `linux/types.h` and generic KVM constants. Integrates with s390 KVM userspace, migration, protected virtualization setup/dump, interrupt injection, memory operation helpers, and device-control attributes.

## Risks and Test Signals
Risks are ABI layout/padding drift, bit ordering for feature/subfunction blocks, large FLIC buffer sizing, PV command reserved fields, and sync-reg alignment. Test signals are KVM selftests, migration/PV tests, mem-op extension tests, interrupt state save/restore, and CPU model attribute round trips.
