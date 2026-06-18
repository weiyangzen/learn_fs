<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/Kbuild

## Purpose
Declares generated syscall headers and generic asm header fallbacks for RISC-V.

## Important APIs, Types, And Functions
Adds `syscall_table_32.h` and `syscall_table_64.h` to syscall generation and maps generic headers such as `early_ioremap.h`, `flat.h`, `fprobe.h`, `kvm_para.h`, spinlock/qrwlock/qspinlock headers, `user.h`, and `vmlinux.lds.h`.

## Control Flow
During header generation, kbuild creates syscall table headers and links or exposes generic asm headers where RISC-V has no custom implementation.

## State And Persistence
State is generated/exported header layout under the build tree.

## Dependencies And Integration Points
Integrated with syscall table generation, generic asm header infrastructure, and consumers including modules and UAPI-adjacent arch code.

## Risks And Edge Cases
Removing a generic mapping can break includes; adding one can mask a needed RISC-V-specific implementation.

## Test Signals
Signals are `make headers_install`, generated syscall tables, and clean compilation of users of generic spinlock/fprobe/KVM para headers.

Source read size: 18 lines, 453 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/Kbuild -->
