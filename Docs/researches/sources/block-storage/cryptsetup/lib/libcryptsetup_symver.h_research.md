# File Research: sources/block-storage/cryptsetup/lib/libcryptsetup_symver.h

This header provides helper macros for exporting multiple ABI versions of the same libcryptsetup public symbol.

Core behavior:
- If compiler attribute support exists, `_CRYPT_SYMVER` uses `__attribute__((__symver__(...)))`.
- Otherwise, for GCC/Clang, it falls back to inline assembler `.symver`.
- `_CRYPT_FUNC` creates local versioned implementation names like `__symbol_v2_5` and binds them to public `CRYPTSETUP_<major>.<minor>` symbol versions.
- `CRYPT_SYMBOL_EXPORT_OLD` exports an old compatible symbol version with single `@`.
- `CRYPT_SYMBOL_EXPORT_NEW` exports the default/latest symbol version with `@@`.
- If symbol versioning is unavailable, old versions become unused static inline definitions and the new version exports as the plain public symbol.

Filesystem/block-storage relevance:
- No direct storage logic is implemented here.
- It protects ABI compatibility for applications linked against older libcryptsetup versions, which is important because cryptsetup is used by system boot, initramfs, storage-management, and filesystem-stack tooling.

Important notes:
- The header explicitly warns not to use these macros for ordinary one-version public symbols.
- It is intended only for functions exported in multiple incompatible ABI versions simultaneously.
