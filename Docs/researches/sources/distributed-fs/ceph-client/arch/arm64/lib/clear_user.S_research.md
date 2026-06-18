# sources/distributed-fs/ceph-client/arch/arm64/lib/clear_user.S

Purpose: implements `__arch_clear_user`, clearing a user memory range and returning the number of bytes not cleared on fault.

Important APIs/types/functions: `__arch_clear_user`, `USER` exception annotations, MOPS `setpt/setmt/setet`, unprivileged `sttr/sttrh/sttrb` stores, and fixup labels that compute residual byte count.

Control flow: computes `end = addr + size`. With MOPS it attempts tagged user clear operations and returns zero on success. The fallback stores eight-byte chunks, then handles 4/2/1 byte tails. Exception fixups translate the faulting pointer and Option A MOPS residual state into the required "bytes not cleared" return value.

State and persistence: writes zeroes to user memory only for successfully accessed bytes. No kernel persistent state changes.

Dependencies/integration: used by uaccess clear paths; depends on `asm-uaccess.h` exception table macros, TTBR0/user access setup by callers, and ARM64 MOPS alternatives.

Risks: residual byte accounting must be exact for partial faults. User access annotations must match actual faulting instructions or `fixup_exception` will not recover. Arithmetic assumes no caller-provided wraparound range is allowed past uaccess validation.

Test signals: clear valid ranges of all small sizes, page-boundary partial faults, inaccessible first byte returning full size, MOPS and non-MOPS CPU paths, and fault injection through usercopy tests.
