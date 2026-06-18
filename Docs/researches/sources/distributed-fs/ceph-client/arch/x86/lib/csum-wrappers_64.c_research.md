# sources/distributed-fs/ceph-client/arch/x86/lib/csum-wrappers_64.c

Purpose: provides C wrappers around the 64-bit assembly checksum-copy routine for user and kernel copy/checksum APIs.

Important APIs/functions: defines `csum_and_copy_from_user`, `csum_and_copy_to_user`, and exported `csum_partial_copy_nocheck`.

Control flow: user wrappers call `might_sleep()`, attempt `user_access_begin()` over the source or destination range, call `csum_partial_copy_generic()` with forced kernel pointers while the uaccess window is open, and then call `user_access_end()`. If access cannot begin, they return zero. The nocheck wrapper directly calls the assembly routine.

State and persistence behavior: no persistent state. Copies to destination buffers and returns an unfolded checksum, with zero indicating failed access or assembly fault.

Dependencies/integration points: depends on asm checksum declarations, Linux uaccess, SMAP helpers, and the assembly symbol in `csum-copy_64.S`. Used by socket and networking code that combines copy and checksum.

Risks: zero is both a valid checksum value and an error fallback at this layer, so higher-level code must use existing API semantics. User access windows must be correctly balanced. The wrappers do not zero destination on failure; assembly behavior is partial-copy oriented.

Test signals: usercopy fault injection, SMAP-enabled builds, checksum-copy comparisons, `might_sleep` context checks, and network receive/send tests involving user buffers.
