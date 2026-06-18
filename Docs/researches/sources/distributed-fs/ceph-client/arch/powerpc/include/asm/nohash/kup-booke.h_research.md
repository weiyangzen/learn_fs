<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/kup-booke.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/kup-booke.h

## Purpose
This header implements BookE KUAP user-access protection primitives by controlling the PID SPR used for address-space matching.

## Important APIs, Types, And Functions
Under `CONFIG_PPC_KUAP`, it defines `__kuap_lock()`, `__kuap_save_and_lock()`, `kuap_user_restore()`, `__kuap_kernel_restore()`, optional `__kuap_get_and_assert_locked()`, `uaccess_begin_booke()`, `uaccess_end_booke()`, `allow_user_access()`, `prevent_user_access()`, `prevent_user_access_return()`, `restore_user_access()`, and `__bad_kuap_fault()`.

## Control Flow
Entry paths save the current PID and set PID to zero to block user access. User-copy windows temporarily restore `current->thread.pid` with an `isync`, then close by writing zero again. Return from interrupt supplies context synchronization for restore paths.

## State And Persistence Behavior
The protected state is the PID SPR and `regs->kuap`. Access windows persist only until `prevent_user_access()` or exception return. Debug mode verifies the locked state by reading the SPR.

## Dependencies And Integration Points
It depends on `asm/reg.h`, `asm/mmu.h`, current task thread PID, exception register state, and MMU feature patching. It integrates with uaccess, exception return, and KUAP fault detection.

## Risks And Edge Cases
Missing `isync` after PID changes can leave stale access permissions. Saving/restoring the wrong PID can either fault valid user copies or permit unintended kernel access to user mappings. Disabled KUAP paths must remain harmless.

## Test Signals
Run powerpc uaccess/KUAP selftests, fault injection around copy_to/from_user, interrupt during user-access windows, and debug KUAP assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/kup-booke.h -->
