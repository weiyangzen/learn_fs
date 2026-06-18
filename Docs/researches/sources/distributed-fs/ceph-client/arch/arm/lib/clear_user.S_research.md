# sources/distributed-fs/ceph-client/arch/arm/lib/clear_user.S

Purpose: implements `arm_clear_user`/`__clear_user_std`, clearing a user memory range and returning the number of bytes not cleared.

Control flow aligns the destination, writes zero by bytes and words through user-access store macros, and uses exception-table fixup `9001` to return the remaining byte count on a fault. State is only the user memory range. Dependencies include uaccess assembler macros, exception table support, and optional override by `uaccess_with_memcpy.c`. Risks are incorrect remaining-count calculation, user access enable/disable context, and alignment edge cases. Test signals include fault-injection on partially mapped ranges, small and unaligned clears, and full zeroing on valid user buffers.
