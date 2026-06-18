# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kup.h

Purpose: Selects and declares Kernel Userspace Access/Execution Protection (KUAP/KUEP) support for PowerPC, providing common masks, setup APIs, and config-dependent stubs.

Important APIs, types, and functions: Defines `KUAP_READ`, `KUAP_WRITE`, `KUAP_READ_WRITE`, declares `kuap_is_disabled()`, includes MMU-family-specific KUP headers, exposes `disable_kuep`, `disable_kuap`, `setup_kup()`, `setup_kuep()`, `setup_kuap()`, and lock/save/assert helper fallbacks depending on architecture implementation macros.

Control flow: Boot setup calls KUP/KUEP initialization, architecture-specific code locks or unlocks user access around copy-to/from-user, and assertion helpers validate that kernel access to userspace is disabled when expected.

State and persistence: Runtime state includes boot disable flags and MMU/register state controlling user access/execution. No persistent storage.

Dependencies and integration points: Integrates uaccess, page table permissions, Book3S 64, Book3S 32, BookE, and 8xx implementations.

Risks: Missing locks around uaccess can leave userspace accessible to kernel code. Overly strict locking can break legitimate copy routines. Config stubs must preserve generic call semantics without silently weakening enabled platforms.

Test signals: Uaccess with KUAP enabled, deliberate missing unlock/lock assertions, KUEP execute-from-user prevention, boot parameters disabling protections, and builds for Book3S64/Book3S32/BookE/8xx.
