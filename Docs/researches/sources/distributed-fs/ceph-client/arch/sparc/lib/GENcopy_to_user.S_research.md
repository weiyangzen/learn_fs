# sources/distributed-fs/ceph-client/arch/sparc/lib/GENcopy_to_user.S

Purpose: Generic SPARC64 raw copy-to-user wrapper. It specializes `GENmemcpy.S` so stores target user address space via `ASI_AIUS` and the generated function is `GENcopy_to_user`.

Important APIs/functions: Defines `EX_ST`, `STORE(type,src,addr)`, `EX_RETVAL(x)`, `PREAMBLE`, and `FUNC_NAME`. The included implementation emits `GENcopy_to_user(dst, src, len)`.

Control flow: The preamble checks `%asi` before copying and falls back to `raw_copy_in_user` when the active ASI is not the expected user ASI. Copying then follows `GENmemcpy.S` alignment, 64-bit, 32-bit, and byte tail paths with exception-table protected stores.

State and persistence: No stored state. It relies on `%asi`, temporary registers, and exception fixup entries.

Dependencies/integration: Depends on `GENmemcpy.S`, user store ASI encoding, `raw_copy_in_user`, and generic copyops patching. Integrated by `Makefile` under `CONFIG_SPARC64`.

Risks/test signals: Store faults must return correct uncopied byte counts and must not corrupt kernel state. Validate with protected/unmapped user destinations, unaligned lengths, KERNEL_DS-style `%asi` checks, and copy-to-user regression tests.
