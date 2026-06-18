## sources/distributed-fs/ceph-client/arch/s390/mm/physaddr.c

Purpose: provides the exported s390 `__phys_addr()` conversion with debug validation.

Important APIs, types, and functions: `__phys_addr(unsigned long x, bool is_31bit)` is exported. It checks that the virtual address is not vmalloc/module space, converts with `__pa_nodebug()`, and optionally asserts the result fits below 2 GiB for 31-bit users.

Control flow: validation happens before and after conversion through `VIRTUAL_BUG_ON()`. The function returns the physical address on success.

State and persistence: no owned state; pure conversion with debug assertions.

Dependencies and integration points: depends on generic mm debug helpers, s390 `__pa_nodebug()`, and callers that need strict physical address conversion.

Risks: callers must not pass vmalloc/module addresses. The 31-bit flag is a hard assertion, not a recoverable error, so misuse can BUG in debug configurations.

Test signals: conversion of direct-map kernel addresses, rejection of vmalloc/module addresses in debug builds, and 31-bit overflow assertion coverage.
