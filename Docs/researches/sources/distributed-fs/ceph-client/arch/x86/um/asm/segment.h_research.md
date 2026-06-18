<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/segment.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/segment.h

## Purpose
`segment.h` defines UML TLS GDT entry range macros for 32-bit thread-area emulation.

## Important APIs, types, and functions
It declares `host_gdt_entry_tls_min` and defines `GDT_ENTRY_TLS_ENTRIES`, `GDT_ENTRY_TLS_MIN`, and `GDT_ENTRY_TLS_MAX`.

## Control flow
TLS code initializes `host_gdt_entry_tls_min` after probing the host, then uses these macros to validate requested TLS slots.

## State and persistence behavior
Global state is `host_gdt_entry_tls_min`, initialized by `tls_32.c`.

## Dependencies and integration points
It depends on host TLS probing in `os-Linux/tls.c` and Linux `user_desc` semantics.

## Risks and edge cases
Wrong host minimum index can make UML write the wrong GDT TLS slots on i386 or x86_64 hosts running 32-bit UML.

## Test signals
Signals are boot log host TLS detection and `set_thread_area`/`get_thread_area` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/segment.h -->
