# sources/distributed-fs/ceph-client/arch/x86/include/asm/uaccess_32.h

Purpose: 32-bit x86 raw user-copy declarations and wrappers used by the common uaccess layer.

Important APIs/types/functions: `__copy_user_ll()`, `__copy_from_user_ll_nocache_nozero()`, `raw_copy_to_user()`, `raw_copy_from_user()`, `copy_from_user_inatomic_nontemporal()`, `clear_user()`, and `__clear_user()`.

Control flow: raw copy wrappers force-cast user pointers and delegate to low-level assembly copy routines. Clearing and nontemporal copy are declared for architecture implementations.

State/persistence: no state; functions return the number of uncopied bytes.

Dependencies/integration: depends on string/page/asm helpers and is included only under `CONFIG_X86_32` by `uaccess.h`.

Risks/test signals: 32-bit copy semantics must match generic usercopy expectations, especially returned residual counts and nozero behavior. Test i386 builds, compat-heavy usercopy tests, page fault during copy, clear_user partial faults, and nontemporal inatomic copies.
