<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/uaccess.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/uaccess.h

**Purpose:** Implements Alpha user-memory access primitives for scalar get/put, raw copy, clear, and string-length/copy helpers.

**Important APIs/types/functions:** `put_user`, `get_user`, `__put_user`, `__get_user`, exception-table macro `EXC`, sized load/store macros, `raw_copy_from_user`, `raw_copy_to_user`, `clear_user`, `strncpy_from_user`, and `strnlen_user`.

**Control flow:** Checked variants call `__access_ok` before inline assembly loads/stores; unchecked variants rely on caller validation. Faulting instructions emit Alpha exception-table fixups that set `-EFAULT` or zero values. Bulk copies delegate to `__copy_user`.

**State and persistence behavior:** No local state; reads/writes user memory and kernel buffers. Exception table entries become part of the kernel image.

**Dependencies and integration points:** Depends on generic access_ok, Alpha byte/word load-store helpers, exception-table handling, and `asm/extable.h`.

**Risks:** Inline assembly and exception fixup encoding are fragile. User pointers share address space with kernel mappings, so access checks and fault handling are the safety boundary.

**Test signals:** lib/uaccess tests, fault-injection around invalid user pointers, copy_to/from_user boundary tests, hardened usercopy, and syscall argument copy tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/uaccess.h -->
