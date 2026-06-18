## sources/distributed-fs/ceph-client/arch/s390/include/asm/uaccess.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/uaccess.h` is a user memory access
primitives in the s390 ceph-client Linux source snapshot. It has 485 lines and 13103 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
raw copy helpers, key-protected copy APIs, get_user/put_user macro families, string/clear helpers,
nofault kernel access, and cmpxchg with storage keys
Important macros/constants: `__S390_UACCESS_H`, `uaccess_kmsan_or_inline`, `INLINE_COPY_FROM_USER`, `INLINE_COPY_TO_USER`, `DEFINE_PUT_USER_NOINSTR(type)`, `DEFINE_PUT_USER(type)`, `__put_user(x, ptr)`, `put_user(x, ptr)`, `DEFINE_GET_USER_NOINSTR(type)`, `DEFINE_GET_USER(type)`, `__get_user(x, ptr)`, `get_user(x, ptr)`, `__mvc_kernel_nofault(dst, src, type, err_label)`, `arch_get_kernel_nofault`, `arch_put_kernel_nofault`.
Important types/layouts: none detected.
Important declarations or inline helpers: `debug_user_asce`, `volatile`, `_copy_from_user_key`, `_copy_to_user_key`, `__put_user_bad`, `goto`, `__get_user_bad`, `strncpy_from_user`, `strnlen_user`, `__clear_user`, `memcpy`, `__s390_kernel_write`, `__mvc_kernel_nofault_bad`, `__cmpxchg_key1`, `__cmpxchg_key2`, `__cmpxchg_key4`, `__cmpxchg_key8`, `__cmpxchg_key16`, `copy_from_user_key`, `copy_to_user_key`; plus 1 more.

### Control Flow
Copy/get/put paths wrap mvcos or specialized inline assembly with exception-table fixups. The fast
path copies directly and returns zero residual/error; fault labels or condition codes compute
remaining bytes or -EFAULT, after which generic usercopy callers decide whether to zero, retry, or
report the fault.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic uaccess, exception tables, KMSAN/KASAN instrumentation, storage-key protection, futex/copy
paths, and hardened usercopy. Direct include dependencies detected here: `linux/pgtable.h`,
`asm/asm-extable.h`, `asm/processor.h`, `asm/extable.h`, `asm/facility.h`, `asm-
generic/access_ok.h`, `asm/asce.h`, `linux/instrumented.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic uaccess, exception tables,
KMSAN/KASAN instrumentation, storage-key protection, futex/copy paths, and hardened usercopy. For
UAPI files, the integration point also includes headers_install and userspace programs compiled
against the exported layout.

### Risks
exception-table, size accounting, or key mistakes can leak kernel data, corrupt userspace, or fault
recursively

### Test Signals
lib/usercopy tests, fault injection, KMSAN/KASAN builds, storage-key tests, and compat syscall
copies
