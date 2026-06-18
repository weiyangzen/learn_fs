# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/meson.build

Defines Meson build composition for the crypto backend static library.

Key points:
- Includes the internal Argon2 subdirectory when `use_internal_argon2` is true.
- Base dependencies include the selected crypto backend library and `clock_gettime`.
- Always includes common sources: Argon2 wrapper, base64, memutils, cipher checks/generic code, CRC32, kernel cipher bridge, storage wrapper, PBKDF benchmark, and UTF helpers.
- Adds the selected backend source dynamically via `crypto_@0@.c`.
- Adds `pbkdf2_generic.c` only when `use_internal_pbkdf2` is true.
- Links internal or external libargon2 depending on Meson options.
- Produces static library `crypto_backend`.

Storage relevance:
- Controls which backend implementation is compiled into cryptsetup while keeping common storage and PBKDF helpers always present.
