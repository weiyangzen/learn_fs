<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/fcntl.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/fcntl.h

Purpose: Defines PowerPC-specific open flag numeric values before importing generic fcntl definitions.

Important APIs/types/functions: `O_DIRECTORY`, `O_NOFOLLOW`, `O_LARGEFILE`, and `O_DIRECT` values.

Control flow: Userspace includes fcntl definitions; these architecture values override/precede generic handling used by syscalls.

State and persistence: No state; constants define syscall ABI bits.

Dependencies and integration points: Integrated with VFS syscall flag decoding and libc headers through `asm-generic/fcntl.h`.

Risks: Flag values are ABI-stable. Collisions with generic flags or wrong octal values alter open behavior.

Test signals: Headers compile and syscall tests for directory/no-follow/largefile/direct-open behavior on PowerPC.

Source read size: 12 lines, 367 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/fcntl.h -->
