## sources/distributed-fs/orangefs/src/client/usrint/stdio-ops.h

Purpose: Declares the libc stdio dispatch table and low-level stream helpers used by OrangeFS usrint's stdio interposition layer.

Important APIs, types, and functions: `struct stdio_ops_s` contains function pointers for file streams, buffered/unlocked I/O, formatted I/O, error/status calls, temp files, directory streams, scandir variants, and file locking. Macros set/test `_IO_FILE` magic and flags. Helper prototypes include `pvfs_set_to_put`, `pvfs_write_buf`, `pvfs_set_to_get`, and `pvfs_read_buf`.

Control flow: No runtime logic. `stdio.c` fills `stdio_ops` using `dlsym(RTLD_NEXT, ...)` and uses these pointers when delegating to glibc streams or when stream redefinition is disabled.

State and persistence: The header declares contracts only. Runtime state lives in `stdio.c`'s `stdio_ops` instance and custom `FILE` objects.

Dependencies and integration points: Tightly coupled to glibc/libio layout via `_G_IO_IO_FILE_VERSION`, `_IO_MAGIC_MASK`, `_IO_*` flags, `FILE`, `DIR`, `dirent`, and scanner signature compatibility macro `PVFS_SCANDIR_VOID`.

Risks and test signals: Direct `_IO_FILE` manipulation is ABI-sensitive across libc versions. Function-pointer signatures must match the target libc exactly, especially scandir comparator types. Test compile/runtime on supported glibc versions, unlocked variants, fortify redirects, and all fallback delegation paths.
