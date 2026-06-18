<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/Kbuild

## Purpose
Declares generated and generic asm headers for Xtensa.

## Important APIs, Types, And Functions
Generates `syscall_table.h` and maps generic headers for `extable.h`, `kvm_para.h`, `mcs_spinlock.h`, `parport.h`, `qrwlock.h`, `qspinlock.h`, `user.h`, and `text-patching.h`.

## Control Flow
Kbuild installs or generates these headers during `headers_install` and internal arch header preparation, using generic implementations where Xtensa has no custom header.

## State And Persistence
Persistent build outputs are generated header files. No runtime state.

## Dependencies And Integration Points
Integrates Xtensa with generic spinlock, extable, parport, KVM paravirt, user, and text patching header contracts.

## Risks And Edge Cases
If Xtensa later needs custom behavior, leaving a generic mapping may hide missing architecture semantics. Missing syscall table generation breaks syscall dispatch builds.

## Test Signals
Run `make archheaders`, headers install, and normal Xtensa builds using qspinlock/qrwlock and syscall table users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/Kbuild -->
