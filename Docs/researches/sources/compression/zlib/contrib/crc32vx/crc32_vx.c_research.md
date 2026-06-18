# sources/compression/zlib/contrib/crc32vx/crc32_vx.c

Purpose: Linux on IBM z Systems hardware-accelerated CRC-32 implementation using z/Architecture Vector Extension Facility.

Important APIs/functions: internal vector routine `crc32_le_vgfm_16`, wrapper `s390_crc32_vx`, one-time setup `s390_crc32_setup`, initializer `s390_crc32_init`, and exported internal function pointer `crc32_z_hook`. Uses vector types `uv16qi`, `uv4si`, `uv2di`, `vec_gfmsum_*`, `vec_perm`, `getauxval(AT_HWCAP)`, and `HWCAP_S390_VX`.

Control flow: compile-time guard rejects Clang versions with a known broken optimization. At runtime the hook initially points to `s390_crc32_init`, which uses `z_once` to set `crc32_z_hook` to vector or generic `crc32_z` based on hardware capabilities. The vector path aligns input, processes 64-byte and 16-byte chunks with GF(2) folding and Barrett reduction, then finishes remaining bytes with generic `crc32_z`.

State and persistence: process-global hook pointer and once flag cache CPU capability selection. No persistent storage.

Dependencies and integration: includes zlib internals via `../../zutil.h` and `crc32_vx_hooks.h`, Linux auxiliary vector APIs, and s390x vector intrinsics. Built into zlib only when configure/CMake detects support.

Risks: architecture-specific pointer casts assume alignment after prealignment and vector type behavior. Runtime hook mutation must be thread-safe via `z_once`; direct external mutation of `crc32_z_hook` would be unsafe. It depends on Linux `getauxval`, so portability is limited.

Test signals: generic zlib checksum tests should pass with the hook enabled; configure/CMake probes catch compiler intrinsic support, while runtime hardware path requires s390x VX hardware or emulation.
