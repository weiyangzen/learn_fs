# sources/distributed-fs/ceph-client/arch/arm/include/asm/string.h

## Purpose
Declares ARM-optimized string/memory routines or selects generic implementations depending on configuration.

## Important APIs, Types, And Functions
Key declarations include extern char * strrchr(const char * s, int c);; extern char * strchr(const char * s, int c);; extern void * memcpy(void *, const void *, __kernel_size_t);; extern void *__memcpy(void *dest, const void *src, __kernel_size_t n);; extern void * memmove(void *, const void *, __kernel_size_t);; extern void *__memmove(void *dest, const void *src, __kernel_size_t n);. Important macros/constants include __ASM_ARM_STRING_H, __HAVE_ARCH_STRRCHR, __HAVE_ARCH_STRCHR, __HAVE_ARCH_MEMCPY, __HAVE_ARCH_MEMMOVE, __HAVE_ARCH_MEMCHR, __HAVE_ARCH_MEMSET, __HAVE_ARCH_MEMSET32, memcpy(dst,, memmove(dst,.

## Control Flow
The C library and kernel helpers bind memcpy, memmove, memset, and string operations to architecture routines when available.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
