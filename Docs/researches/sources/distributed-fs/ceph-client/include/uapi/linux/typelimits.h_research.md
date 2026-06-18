# sources/distributed-fs/ceph-client/include/uapi/linux/typelimits.h

Purpose: Provides kernel UAPI integer limit macros without relying on libc headers.

Important APIs/types/functions: `__KERNEL_INT_MAX` computes signed int max from `~0U >> 1`; `__KERNEL_INT_MIN` derives the minimum as negative max minus one.

Control flow: None; compile-time constants only.

State and persistence behavior: No runtime state.

Dependencies and integration points: Used by UAPI headers that need portable integer bounds in userspace-visible definitions.

Risks: Assumes two's-complement-like signed integer range used by supported Linux ABIs. Macro names are internal-style UAPI and should not conflict with libc `INT_MAX`.

Test signals: Compile under supported architectures and C modes; static assertions should match libc `INT_MAX`/`INT_MIN`.
