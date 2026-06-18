## sources/distributed-fs/beegfs/client_module/source/os/OsDeps.h

**Purpose:** Declares OS-dependent utility helpers and inline allocation/string wrappers used throughout the kernel client.

**Important APIs/types/functions:** In debug builds declares stack-trace helpers. Defines `os_kmalloc`, `os_kzalloc`, and `os_strnicmp`.

**Control flow:** Allocation wrappers first attempt `kmalloc`/`kzalloc` with `GFP_NOFS`; if allocation fails, they log a warning and retry with `__GFP_NOFAIL`. `os_strnicmp` uses `strnicmp` when available, otherwise `strncasecmp`.

**State and persistence behavior:** No state is stored. Allocation wrappers can block indefinitely on no-fail retry, which is an intentional emergency behavior for call sites that cannot handle NULL.

**Dependencies and integration points:** Included by many BeeGFS kernel client files, especially constructors and small data-structure helpers. Relies on `FhgfsOps_versions.h` feature macros and core kernel module/slab headers.

**Risks:** `__GFP_NOFAIL` in `GFP_NOFS` context can cause long stalls under memory pressure; call sites using these wrappers may assume success and skip NULL handling. The warning uses `%d` for size after cast to int, truncating very large sizes in diagnostics.

**Test signals:** Low-memory/fault-injection tests should validate that critical paths tolerate stalls, constructors work with wrapper allocations, and string comparison behavior is stable across kernel versions.
