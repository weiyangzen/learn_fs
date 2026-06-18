# sources/distributed-fs/orangefs/src/common/misc/pvfs2-internal.h

Purpose: Central internal compatibility header for non-kernel OrangeFS code, defining initialization attributes, malloc redirection policy, portable printf/scanf helpers, and canonical internal key strings used by metadata and xattr paths.

Important APIs and definitions: Defines `GCC_CONSTRUCTOR`, `GCC_DESTRUCTOR`, `GCC_UNUSED`, `PVFS_INIT`, initialization/cleanup priority constants, `llu`/`lld` cast macros, `SCANF_lld`, metadata key strings like `ROOT_HANDLE_KEYSTR`, `DIRECTORY_ENTRY_KEYSTR`, `METAFILE_DIST_KEYSTR`, distributed-directory keys, `SPECIAL_PREFIX` and `user.pvfs2.*` xattr names, plus `IO_MAX_REGIONS`.

Control flow: Header logic is compile-time conditional. Non-kernel builds include `pvfs2-config.h` and `pint-malloc.h`, optionally disable malloc redefinition, and force `PVFS_INIT(f)` to call `f()` at entry points. Integer-format macros branch on `BITS_PER_LONG` or configured `SIZEOF_LONG_INT`.

State and persistence: No runtime state is owned here, but key-string constants define persistent storage names for server metadata and optional user xattrs. Changing these constants would affect on-disk or keyval compatibility.

Dependencies and integration points: Included widely throughout OrangeFS internals. It bridges generated configure values, Linux kernel type definitions, malloc wrappers, metadata servers, clients, xattr tools, and request code needing stable key names.

Risks: Forced `PVFS_INIT(f)` means entry points may repeatedly call initialization checks; behavior depends on idempotent init functions. Format macros intentionally cast on some architectures, which can hide incorrect format strings on 64-bit builds. Key lengths include NUL bytes and must stay synchronized with string literals.

Test signals: Compile with GCC pre-4.4, modern GCC, non-GCC, kernel, 32-bit, and 64-bit configurations. Add static assertions or tests for every key length and verify xattr/keyval lookup compatibility with stored metadata.
