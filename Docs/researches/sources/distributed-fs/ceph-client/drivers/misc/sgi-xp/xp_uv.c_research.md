# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xp_uv.c

Purpose: supplies UV-specific implementations for XP address translation, remote memory copy, CPU-to-NASID conversion, and BIOS memory protection operations. It connects XP/XPC transport to GRU kernel services.

Important APIs/functions: `xp_init_uv()` installs UV hooks into XP globals; `xp_exit_uv()` validates platform exit. Internal hook implementations include `xp_pa_uv()`, `xp_socket_pa_uv()`, `xp_remote_memcpy_uv()`, `xp_remote_mmr_read()`, `xp_cpu_to_nasid_uv()`, `xp_expand_memprotect_uv()`, and `xp_restrict_memprotect_uv()`.

Control flow: initialization checks `is_uv_system()`, sets partition count and partition/region identity, then assigns function pointers. Remote copies route MMR-space reads through `gru_read_gpa()` with an 8-byte constraint; other memory copies use `gru_copy_gpa()`. BIOS memory protection hooks call `uv_bios_change_memprotect()` to allow or restrict access.

State and persistence: no private persistent state. It mutates XP global function pointers and exported partition metadata during init.

Dependencies and integration: depends on UV hub/BIOS APIs and `../sgi-gru/grukservices.h`. XPC partition discovery and reserved-page reads use `xp_remote_memcpy`, so GRU service availability is a runtime prerequisite for cross-partition operation.

Risks: failures in GRU copy/read map to `xpGruCopyError` after logging. `xp_remote_mmr_read()` asserts source is MMR space and length is exactly 8 bytes. BIOS memory-protection changes are platform-specific and return `xpBiosError` on firmware failure. Non-x86_64 paths are explicitly unsupported.

Test signals: UV boot/module init, remote reserved-page copy, MMR read path, GRU copy failure injection, BIOS memprotect allow/restrict calls, and non-UV init returning unsupported.
