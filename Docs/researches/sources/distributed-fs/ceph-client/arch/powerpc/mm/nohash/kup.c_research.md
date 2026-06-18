# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/kup.c

Purpose: initializes Kernel Userspace Access Protection for nohash PowerPC MMUs.

Important APIs and control flow: `setup_kuap()` either clears `MMU_FTR_KUAP` on the boot CPU when disabled, or logs activation and calls `prevent_user_access(KUAP_READ_WRITE)` to start with user read/write access blocked.

State and dependencies: persistent state is the CPU spec MMU feature bit and hardware/software KUAP state. It depends on `CONFIG_PPC_KUAP`, SMP boot CPU checks, and `asm/kup.h` access-control primitives. Risks are leaving user access enabled during boot, inconsistent feature bits across CPUs, and disabling KUAP through `nosmap` unexpectedly widening kernel access. Test signals include KUAP boot logs, copy_to/from_user success, deliberate missing allow-user-access fault tests, and nosmap boot behavior.
