# sources/distributed-fs/ceph-client/arch/x86/lib/putuser.S

## Purpose
This assembly file implements the out-of-line x86 `__put_user_*` helpers used by uaccess inline assembly to store 1, 2, 4, or 8 byte values into user memory while returning an error code through a nonstandard register ABI.

## Important APIs, Types, and Functions
Exported entry points are `__put_user_1`, `__put_user_2`, `__put_user_4`, `__put_user_8`, and nocheck variants `__put_user_nocheck_1`, `__put_user_nocheck_2`, `__put_user_nocheck_4`, and `__put_user_nocheck_8`. The shared failure path is `__put_user_handle_exception`. The `check_range` macro performs bounds checks on 32-bit and sign/canonicalization logic on 64-bit. The code uses `ASM_STAC`, `ASM_CLAC`, `ANNOTATE_NOENDBR`, `_ASM_EXTABLE_UA`, and x86 linkage macros.

## Control Flow
Checked helpers validate the user address range, enable SMAP user access with STAC, perform the store, clear access with CLAC, zero `%ecx`, and return. Nocheck variants skip the range check but still use STAC/CLAC and exception-table fixups. Any store fault jumps through the uaccess exception table to `__put_user_handle_exception`, which clears SMAP access and returns `-EFAULT` in `%ecx`.

## State and Persistence
The file has no persistent state. It temporarily mutates AC/SMap access state and writes caller-supplied data into user memory. The ABI preserves registers except for the documented error register and clobbers.

## Dependencies and Integration Points
It integrates with x86 uaccess macros, SMAP, exception tables, objtool/IBT annotations, kernel errno values, and 32/64-bit register naming macros. It is on a critical syscall and copy-to-user path.

## Risks and Test Signals
Risks include ABI drift with inline callers, missing CLAC on faults, incorrect range checks near `TASK_SIZE_MAX`, split 64-bit writes on i386, and exception-table label mistakes. Test signals include uaccess selftests, fault injection on invalid user pointers, SMAP-enabled boot tests, 32-bit and 64-bit builds, objtool validation, and syscall paths that use `put_user()`.
