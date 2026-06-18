# File Research: sources/block-storage/cryptsetup/lib/meson.build

This Meson build file defines the cryptsetup library build.

Main build structure:
- Enters `crypto_backend` subdirectory.
- Defines `libutils_io` static library from `utils_io.c`.
- Sets the symbol version script path `libcryptsetup.sym`.
- Defines `libcryptsetup_deps`: crypto backend library, uuid, devmapper, argon2, json-c, blkid, and dl.
- Defines `libcryptsetup_sources`, including the LUKS2 files in this group:
  - `luks2/luks2_reencrypt.c`
  - `luks2/luks2_reencrypt_digest.c`
  - `luks2/luks2_segment.c`
  - `luks2/luks2_token.c`
  - `luks2/luks2_token_keyring.c`
- Builds either a static `cryptsetup` library when `enable_static` is set or a shared `cryptsetup` library with versioning and linker version script.
- Links both library variants with crypto backend and `libutils_io`.
- Defines helper file lists for tools and ssh token builds.
- Installs `libcryptsetup.h`.
- Generates pkg-config metadata for `libcryptsetup`.

This file is the integration point that ensures the reencryption, segment, token, and random support sources are compiled into the core library.
