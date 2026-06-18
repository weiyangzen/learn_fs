<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/desc.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/desc.h

## Purpose
`desc.h` provides the one descriptor predicate UML needs: checking whether an i386 TLS/LDT `user_desc` is empty.

## Important APIs, types, and functions
The API is `LDT_empty(info)`, comparing base, limit, contents, read/exec, 32-bit, page-limit, present, and usable fields.

## Control flow
TLS code uses the macro to identify cleared descriptors and decide whether to reject or synthesize an empty entry.

## State and persistence behavior
No state exists.

## Dependencies and integration points
It depends on Linux `struct user_desc` layout from x86 LDT headers.

## Risks and edge cases
Field-layout drift would misclassify TLS entries, breaking `set_thread_area` emulation.

## Test signals
Signals are 32-bit UML TLS/syscall tests and ptrace thread-area operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/desc.h -->
