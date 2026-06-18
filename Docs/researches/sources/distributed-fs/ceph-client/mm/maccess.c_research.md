# sources/distributed-fs/ceph-client/mm/maccess.c

## Purpose

`maccess.c` implements best-effort kernel and user memory access helpers that do not take normal page faults. These helpers are used by tracing, diagnostics, probes, and other contexts where a fault must be converted into an error rather than handled through the normal fault path.

## Important APIs, types, and functions

Kernel-source helpers are `copy_from_kernel_nofault_allowed()` (weak arch/security override), `copy_from_kernel_nofault()`, `copy_to_kernel_nofault()`, and `strncpy_from_kernel_nofault()`. User-source helpers are `copy_from_user_nofault()`, `copy_to_user_nofault()`, `strncpy_from_user_nofault()`, and `strnlen_user_nofault()`. `__copy_overflow()` reports compile-time/object-size copy overflow detections. Exported symbols include `copy_from_kernel_nofault`, `copy_from_user_nofault`, `copy_to_user_nofault`, and `__copy_overflow`.

The typed loop macros use `__get_kernel_nofault()` and `__put_kernel_nofault()` in decreasing word sizes (`u64`, `u32`, `u16`, `u8`) when alignment permits. KMSAN and instrumentation hooks are present so nofault operations still participate in memory checking and write instrumentation.

## Control flow

Kernel reads first reject disallowed ranges through `copy_from_kernel_nofault_allowed()`, disable page faults, copy in aligned chunks, then re-enable page faults and return `0` or `-EFAULT`. Kernel writes similarly disable faults and use `__put_kernel_nofault()`, returning `-EFAULT` if any store faults.

`strncpy_from_kernel_nofault()` copies byte-by-byte until NUL or count, always terminates the destination on success, returns bytes consumed including the terminating NUL when found, returns `count` for truncation, and returns `-EFAULT` with `dst[0] = '\0'` on fault. User copies validate `access_ok()` or `__access_ok()` and, for user reads, `nmi_uaccess_okay()` before using inatomic copy helpers inside a pagefault-disabled section. User string helpers wrap `strncpy_from_user()` and `strnlen_user()` with page faults disabled, then normalize truncation and success return values.

## State and persistence behavior

The file maintains no persistent data. All state is on the stack or in caller-provided buffers. The important process-wide side effect is transient `pagefault_disable()`/`pagefault_enable()` nesting around unsafe access. `__copy_overflow()` emits a warning but does not maintain state.

## Dependencies and integration points

The implementation depends on architecture-provided nofault get/put primitives, user access validation, pagefault disable accounting, KMSAN, compiler object-size checking, and low-level `__copy_*_user_inatomic()` helpers. Architecture code can override `copy_from_kernel_nofault_allowed()` to reject ranges such as user aliases, firmware holes, or other unsafe kernel addresses.

## Risks and edge cases

These helpers do not pin memory and provide no stability guarantee: a successful copy only means the bytes were readable/writable at that moment. They must not be used as permission checks or to access arbitrary user memory without higher-level validation. Return conventions differ between raw copy helpers (`0` or negative errno) and string helpers (length/truncation or fault code). Missing destination space for forced NUL termination would be a caller bug. NMI and IRQ contexts require architecture support; the user-read path explicitly rejects when `nmi_uaccess_okay()` fails.

## Test signals

Useful tests cover valid and invalid kernel addresses, architecture-specific disallowed ranges returning `-ERANGE`, unaligned source/destination copies on platforms without efficient unaligned access, user addresses failing `access_ok()`, faulting user pages returning `-EFAULT`, string truncation and termination behavior, NMI-context rejection where applicable, KMSAN/instrumentation reports, and compile-time overflow warnings routed through `__copy_overflow()`.
