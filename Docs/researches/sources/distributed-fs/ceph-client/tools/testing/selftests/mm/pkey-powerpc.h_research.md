# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-powerpc.h

Purpose: provides powerpc64-specific protection-key register, permission, page-size, and reserved-key behavior for the generic pkey selftests.

Important APIs and functions: defines AMR access via `mfspr/mtspr 0xd`, powerpc permission encodings, `NR_PKEYS`, platform-specific reserved-key counts, `arch_is_powervm()`, `get_arch_reserved_keys()`, no-op generation macros, and `malloc_pkey_with_mprotect_subpage()` using `__NR_subpage_prot`.

Control flow and state: included via `pkey-helpers.h`; generic tests call inline register helpers, bit positioning, execute-only expectations, and the optional subpage allocator backend. It reads firmware/device-tree paths and mutates per-thread AMR.

Dependencies and risks: depends on powerpc `ucontext` layout, pkey and subpage syscalls, and `/sys/firmware/devicetree`. Reserved-key math differs by page size and platform; bad detection can invalidate allocation-exhaustion expectations.
