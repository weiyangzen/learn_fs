# sources/distributed-fs/ceph-client/arch/s390/include/asm/runtime-const.h

Purpose: This header implements s390 runtime constant patching for pointer loads and shift immediates.

Important APIs/types/functions: `runtime_const_ptr(sym)`, `runtime_const_shift_right_32(val, sym)`, `runtime_const_init(type, sym)`, `__runtime_fixup_32()`, `__runtime_fixup_ptr()`, `__runtime_fixup_shift()`, and `runtime_const_fixup()` are defined.

Control flow: Code emits placeholder instructions and a section containing relative offsets to those instructions. Initialization walks the section for a symbol and patches the immediate fields with the runtime value using `s390_kernel_write()`.

State and persistence: Persistent state is patched kernel text and the runtime metadata sections `runtime_ptr_*` and `runtime_shift_*`.

Dependencies and integration points: It depends on safe kernel text write support from uaccess and is used by code needing runtime-known constants without an extra memory load.

Risks and test signals: Patch offsets and instruction field masks must match the exact generated instructions. Tests should include boot-time fixups, objdump of placeholders, KASLR/runtime symbol values, read-only text write safety, and users of runtime shift constants.
