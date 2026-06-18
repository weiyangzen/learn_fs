# sources/distributed-fs/ceph-client/arch/sparc/kernel/sys32.S

Purpose: implements a tiny 32-bit compatibility assembly wrapper for `mmap2`.

Important APIs/symbols: defines global `sys32_mmap2`, branches to `sys_mmap`, and shifts `%o5` by 12 to convert mmap2 page units into byte offset units expected by `sys_mmap`.

Control flow: the wrapper loads the `sys_mmap` address, jumps without a normal call/return stack disturbance, and uses the delay slot to scale the sixth argument.

State and persistence: no state is stored; it only transforms syscall arguments.

Dependencies and integration points: used by the 64-bit kernel compat syscall table for 32-bit applications. Depends on SPARC syscall register calling convention and `sys_mmap` semantics.

Risks: offset scaling is ABI-sensitive. The comment notes avoiding call-as-jump because it breaks return-stack behavior.

Test signals: 32-bit `mmap2()` on a 64-bit kernel with nonzero page offsets, large offsets, and tracing enabled should map the same file locations as other architectures' compat mmap2.
