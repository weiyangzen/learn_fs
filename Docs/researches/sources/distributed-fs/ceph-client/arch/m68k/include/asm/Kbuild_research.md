<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/Kbuild

## Purpose
This Kbuild fragment declares generated and generic asm headers for the m68k architecture include tree. It tells the kernel header build that `syscall_table.h` is generated and that several asm headers are satisfied by `asm-generic`.

## Important APIs, Types, And Functions
- `generated-y += syscall_table.h` registers the generated syscall table header.
- `generic-y += extable.h`, `kvm_para.h`, `mcs_spinlock.h`, `spinlock.h`, and `text-patching.h` select generic implementations.

## Control Flow
There is no runtime control flow. The kernel build system reads these variables while exporting or preparing architecture headers.

## State And Persistence Behavior
The file persists build metadata only. It does not define kernel state, but changes alter which headers are generated or delegated to generic asm code.

## Dependencies And Integration Points
It integrates with Kbuild's `scripts/Makefile.asm-generic` handling and with generated header production for m68k syscalls.

## Risks And Edge Cases
Removing a `generic-y` entry can make include resolution fail. Adding a generated header without a matching generator can break `headers_install` or normal builds.

## Test Signals
Run `make ARCH=m68k headers_check` or an m68k kernel build and verify generated `asm/syscall_table.h` and generic asm includes resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/Kbuild -->
