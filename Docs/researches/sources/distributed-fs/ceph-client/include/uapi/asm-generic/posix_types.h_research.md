# sources/distributed-fs/ceph-client/include/uapi/asm-generic/posix_types.h

Purpose: Defines generic kernel POSIX-compatible typedefs exported to user space.

Important APIs/types/functions: Provides `__kernel_long_t`, `__kernel_ino_t`, `__kernel_mode_t`, pid/uid/gid types, `__kernel_size_t`/`ssize_t`/`ptrdiff_t` selected by `__BITS_PER_LONG`, `__kernel_fsid_t`, offsets, time types, clock/timer ids, caddr, and 16-bit uid/gid aliases.

Control flow: Many typedefs are guarded so architectures can override before inclusion. `__BITS_PER_LONG` controls size-related typedefs.

State/persistence: No runtime state; typedefs determine UAPI struct layout.

Dependencies/integration: Includes `asm/bitsperlong.h`; foundational for many UAPI headers.

Risks: Namespace pollution and ABI layout are key risks. Changing typedef widths breaks user-kernel structures.

Test signals: Headers compile tests and ABI layout checks for structs using these typedefs on 32-bit/64-bit targets.
