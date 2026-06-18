# sources/distributed-fs/ceph-client/include/linux/secretmem.h

Purpose: `secretmem.h` exposes recognition helpers for secret memory mappings. Secretmem provides memory that is intentionally inaccessible to the kernel direct map and guarded from ordinary core dump or mapping behavior by implementation code.

Important APIs/types/functions: With `CONFIG_SECRETMEM`, it declares `secretmem_aops`, `secretmem_mapping()`, `vma_is_secretmem()`, and `secretmem_active()`. Disabled builds return false for all helpers.

Control flow: Callers test an `address_space` through `secretmem_mapping()` or a VMA through `vma_is_secretmem()` before applying special handling. `secretmem_active()` lets subsystems cheaply decide whether any secretmem handling may be needed.

State and persistence behavior: The header owns no state. It compares `mapping->a_ops` to the secretmem address-space operations and delegates VMA/activity state to implementation code. Secret memory lifetime follows file/mapping/VMA lifetime.

Dependencies and integration points: It integrates with MM, VMA walking, address-space operations, page fault handling, and memory accounting. Consumers include dump, migration, reclaim, and other code that must avoid exposing secret pages.

Risks: Pointer comparison to `secretmem_aops` requires mappings to be initialized correctly. Disabled stubs must preserve behavior where secretmem cannot exist. Callers must not infer page secrecy solely from unrelated VMA flags.

Test signals: Build with and without `CONFIG_SECRETMEM`, create secretmem mappings, validate `vma_is_secretmem()` and `secretmem_mapping()`, test fork/mmap/munmap lifecycle, and ensure dump/reclaim paths respect secret pages.
