# sources/distributed-fs/ceph-client/include/linux/uaccess.h

## Purpose
Defines generic user-access wrappers around architecture raw copy/get/put primitives, including object-size hardening, fault injection, instrumentation, speculative-access barriers, pagefault disable guards, nofault copies, ABI-compatible struct copy helpers, and scoped unsafe user access macros.

## Important APIs, Types, And Functions
Core APIs include `copy_from_user()`, `copy_to_user()`, `__copy_from_user()`, `__copy_to_user()`, inatomic variants, `_inline_copy_from_user()`, `_inline_copy_to_user()`, `copy_mc_to_kernel()`, `pagefault_disable/enable()`, `pagefault_disabled()`, `faulthandler_disabled()`, `probe_subpage_writeable()`, `copy_from_user_inatomic_nontemporal()`, `check_zeroed_user()`, `copy_struct_from_user()`, `copy_struct_to_user()`, kernel/user nofault copy/string helpers, `get_kernel_nofault()`, unsafe get/put/copy macros, scoped user access macros, `get_user_inline()`, `put_user_inline()`, and hardened usercopy abort hook.

## Control Flow
Normal copies first validate compile/runtime copy size, check or mask user addresses, apply speculation barriers after `access_ok()`, instrument the copy, call arch raw copy, and return bytes not copied. Only `copy_from_user()` zero-pads the destination tail on short copy. Struct-copy helpers compare user and kernel struct sizes: old userspace gets zero-filled trailing kernel fields, newer userspace must provide zeroed unknown fields, and smaller user output receives only the known prefix with optional trailing-data notification.

## State, Persistence, And Dependencies
Persistent state touched here is `current->pagefault_disabled`. Other behavior is controlled by arch `asm/uaccess.h`, hardened usercopy static keys, fault injection, instrumentation, nospec, scheduler context, and copy-size checking.

## Integration Points
Every syscall, ioctl, procfs/sysfs binary path, and driver userspace ABI uses these helpers. Architecture ports provide raw primitives and optional masked/scoped access implementations.

## Risks And Test Signals
Risks include unchecked return values from non-zeroing `__copy_from_user()`, missing `access_ok()` around inatomic copies, incorrect struct ABI size rules, speculative access after failed checks, nesting scoped access illegally, and pagefault-disable misuse. Test signals include hardened usercopy tests, fault-injection short copies, KASAN/KMSAN instrumentation, struct versioning ABI tests, nofault copy tests, MTE/subpage probing, and 32/64-bit compat ioctl coverage.
